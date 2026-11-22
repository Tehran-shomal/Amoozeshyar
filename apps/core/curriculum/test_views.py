import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.core.models import (
    Constant,
    Curriculum,
    Department,
    Faculty,
    Field,
    Lesson,
    Person,
    Student,
    SystemSetting,
    Teacher,
)


class CurriculumAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # =====================================================
        # Faculties
        # =====================================================
        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده آزمون چارت",
            faculty_code="CUR-FAC-1",
        )

        cls.other_faculty = Faculty.objects.create(
            faculty_name="دانشکده دیگر آزمون چارت",
            faculty_code="CUR-FAC-2",
        )

        # =====================================================
        # Departments
        # =====================================================
        cls.department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه کامپیوتر آزمون چارت",
            department_code="CUR-DEP-1",
        )

        cls.other_department = Department.objects.create(
            faculty=cls.other_faculty,
            department_name="گروه ریاضی آزمون چارت",
            department_code="CUR-DEP-2",
        )

        # =====================================================
        # Fields
        # =====================================================
        cls.field = Field.objects.create(
            department=cls.department,
            field_name="مهندسی کامپیوتر آزمون چارت",
            field_code="CUR-FIELD-1",
        )

        cls.second_field = Field.objects.create(
            department=cls.department,
            field_name="فناوری اطلاعات آزمون چارت",
            field_code="CUR-FIELD-2",
        )

        cls.other_field = Field.objects.create(
            department=cls.other_department,
            field_name="ریاضی آزمون چارت",
            field_code="CUR-FIELD-3",
        )

        # =====================================================
        # Requirement type
        # =====================================================
        cls.requirement_type = Constant.objects.create(
            category="requirement_type",
            code="CUR-COMPULSORY",
            label="اجباری",
        )

        # =====================================================
        # Lessons
        # =====================================================
        cls.lesson = Lesson.objects.create(
            lesson_code="CUR-101",
            title="برنامه‌نویسی آزمون",
            theory_units=3,
            practical_units=0,
            department=cls.department,
        )

        cls.second_lesson = Lesson.objects.create(
            lesson_code="CUR-102",
            title="پایگاه داده آزمون",
            theory_units=2,
            practical_units=1,
            department=cls.department,
        )

        cls.other_lesson = Lesson.objects.create(
            lesson_code="CUR-201",
            title="ریاضیات آزمون",
            theory_units=3,
            practical_units=0,
            department=cls.other_department,
        )

        # =====================================================
        # Admin
        # =====================================================
        cls.admin = Person.objects.create_user(
            username="curriculum-admin",
            password="TestPassword@123",
            first_name="مدیر",
            last_name="آزمون",
            email="curriculum-admin@example.com",
            national_id="9920000001",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
            is_staff=True,
            is_superuser=True,
        )

        # =====================================================
        # Student
        # =====================================================
        cls.student_person = Person.objects.create_user(
            username="curriculum-student",
            password="TestPassword@123",
            first_name="دانشجوی",
            last_name="آزمون",
            email="curriculum-student@example.com",
            national_id="9920000002",
            birth_date=date(2002, 1, 1),
            birth_place="تهران",
        )

        # یک دانشجو با دو پروفایل و دو رشته
        Student.objects.create(
            person=cls.student_person,
            student_code="CUR-ST-001",
            field=cls.field,
            application_date=date(2022, 9, 23),
        )

        Student.objects.create(
            person=cls.student_person,
            student_code="CUR-ST-002",
            field=cls.second_field,
            application_date=date(2023, 9, 23),
        )

        # =====================================================
        # Teacher
        # =====================================================
        cls.teacher_person = Person.objects.create_user(
            username="curriculum-teacher",
            password="TestPassword@123",
            first_name="استاد",
            last_name="آزمون",
            email="curriculum-teacher@example.com",
            national_id="9920000003",
            birth_date=date(1980, 2, 2),
            birth_place="تهران",
        )

        Teacher.objects.create(
            person=cls.teacher_person,
            teacher_code="CUR-TEACHER-001",
            department=cls.department,
            hire_date=date(2010, 9, 1),
        )

        # =====================================================
        # Authenticated user without an application role
        # =====================================================
        cls.normal_person = Person.objects.create_user(
            username="curriculum-normal-user",
            password="TestPassword@123",
            first_name="کاربر",
            last_name="عادی",
            email="curriculum-normal@example.com",
            national_id="9920000004",
            birth_date=date(1990, 1, 1),
            birth_place="تهران",
        )

        # =====================================================
        # Curriculum records
        # =====================================================
        cls.student_curriculum = Curriculum.objects.create(
            field=cls.field,
            lesson=cls.lesson,
            requirement_type=cls.requirement_type,
            recommended_term=1,
            calculated_units=3,
            is_active=True,
        )

        cls.second_student_curriculum = Curriculum.objects.create(
            field=cls.second_field,
            lesson=cls.second_lesson,
            recommended_term=2,
            calculated_units=3,
            is_active=True,
        )

        cls.other_department_curriculum = Curriculum.objects.create(
            field=cls.other_field,
            lesson=cls.other_lesson,
            recommended_term=1,
            calculated_units=3,
            is_active=True,
        )

        cls.inactive_curriculum = Curriculum.objects.create(
            field=cls.field,
            lesson=Lesson.objects.create(
                lesson_code="CUR-103",
                title="درس غیرفعال آزمون",
                theory_units=2,
                practical_units=0,
                department=cls.department,
            ),
            recommended_term=3,
            calculated_units=2,
            is_active=False,
        )

    # =========================================================
    # Helper methods
    # =========================================================

    def login_as(self, user):
        self.client.force_login(user)

    def set_pagination_setting(self, key, value):
        integer_type, _ = Constant.objects.get_or_create(
            category="data_type",
            code="integer",
            defaults={"label": "عدد صحیح"},
        )

        SystemSetting.objects.update_or_create(
            setting_key=key,
            defaults={
                "setting_value": str(value),
                "data_type": integer_type,
            },
        )

    def curriculum_list_url(self):
        return reverse("curriculum:curriculum-list")

    def curriculum_create_url(self):
        return reverse("curriculum:curriculum-create")

    def curriculum_detail_url(self, curriculum):
        return reverse(
            "curriculum:curriculum-detail",
            kwargs={"curriculum_id": curriculum.curriculum_id},
        )

    def curriculum_update_url(self, curriculum):
        return reverse(
            "curriculum:curriculum-update",
            kwargs={"curriculum_id": curriculum.curriculum_id},
        )

    def curriculum_activate_url(self, curriculum):
        return reverse(
            "curriculum:curriculum-activate",
            kwargs={"curriculum_id": curriculum.curriculum_id},
        )

    def curriculum_deactivate_url(self, curriculum):
        return reverse(
            "curriculum:curriculum-deactivate",
            kwargs={"curriculum_id": curriculum.curriculum_id},
        )

    def json_post(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    # =========================================================
    # Authentication and permissions
    # =========================================================

    def test_anonymous_user_cannot_access_curriculum_list(self):
        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "authentication_required",
        )

    def test_authenticated_user_without_role_cannot_access_curriculum(self):
        self.login_as(self.normal_person)

        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error"]["code"],
            "permission_denied",
        )

    def test_student_cannot_create_curriculum(self):
        self.login_as(self.student_person)

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": self.field.pk,
                "lesson_id": self.lesson.pk,
                "recommended_term": 1,
                "calculated_units": 3,
            },
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_cannot_create_curriculum(self):
        self.login_as(self.teacher_person)

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": self.field.pk,
                "lesson_id": self.lesson.pk,
                "recommended_term": 1,
                "calculated_units": 3,
            },
        )

        self.assertEqual(response.status_code, 403)

    # =========================================================
    # Student access tests
    # =========================================================

    def test_student_sees_only_active_curriculums_of_own_fields(self):
        self.login_as(self.student_person)

        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 200)

        records = response.json()["curriculums"]
        returned_ids = {record["id"] for record in records}

        self.assertEqual(
            returned_ids,
            {
                self.student_curriculum.curriculum_id,
                self.second_student_curriculum.curriculum_id,
            },
        )

        self.assertNotIn(
            self.other_department_curriculum.curriculum_id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_curriculum.curriculum_id,
            returned_ids,
        )

    def test_student_can_filter_by_second_own_field(self):
        self.login_as(self.student_person)

        response = self.client.get(
            self.curriculum_list_url(),
            {"field_id": self.second_field.pk},
        )

        self.assertEqual(response.status_code, 200)

        records = response.json()["curriculums"]

        self.assertEqual(len(records), 1)
        self.assertEqual(
            records[0]["id"],
            self.second_student_curriculum.curriculum_id,
        )

    def test_student_cannot_bypass_scope_using_field_filter(self):
        self.login_as(self.student_person)

        response = self.client.get(
            self.curriculum_list_url(),
            {"field_id": self.other_field.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)
        self.assertEqual(response.json()["curriculums"], [])

    def test_student_cannot_access_inactive_curriculum_with_filter(self):
        self.login_as(self.student_person)

        response = self.client.get(
            self.curriculum_list_url(),
            {"is_active": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_student_cannot_access_other_field_detail(self):
        self.login_as(self.student_person)

        response = self.client.get(
            self.curriculum_detail_url(
                self.other_department_curriculum
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_student_cannot_access_inactive_curriculum_detail(self):
        self.login_as(self.student_person)

        response = self.client.get(
            self.curriculum_detail_url(self.inactive_curriculum)
        )

        self.assertEqual(response.status_code, 404)

    # =========================================================
    # Teacher access tests
    # =========================================================

    def test_teacher_sees_active_curriculums_in_own_department(self):
        self.login_as(self.teacher_person)

        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 200)

        records = response.json()["curriculums"]
        returned_ids = {record["id"] for record in records}

        self.assertEqual(
            returned_ids,
            {
                self.student_curriculum.curriculum_id,
                self.second_student_curriculum.curriculum_id,
            },
        )

        self.assertNotIn(
            self.other_department_curriculum.curriculum_id,
            returned_ids,
        )

        self.assertNotIn(
            self.inactive_curriculum.curriculum_id,
            returned_ids,
        )

    def test_teacher_cannot_access_other_department_detail(self):
        self.login_as(self.teacher_person)

        response = self.client.get(
            self.curriculum_detail_url(
                self.other_department_curriculum
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_teacher_cannot_access_inactive_curriculum(self):
        self.login_as(self.teacher_person)

        response = self.client.get(
            self.curriculum_list_url(),
            {"is_active": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    # =========================================================
    # Admin list and filter tests
    # =========================================================

    def test_admin_can_see_active_and_inactive_curriculums(self):
        self.login_as(self.admin)

        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 4)

    def test_admin_can_filter_active_curriculums(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_list_url(),
            {"is_active": "true"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 3)

    def test_admin_can_filter_inactive_curriculums(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_list_url(),
            {"is_active": "false"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        self.assertEqual(
            response.json()["curriculums"][0]["id"],
            self.inactive_curriculum.curriculum_id,
        )

    def test_invalid_is_active_filter_returns_400(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_list_url(),
            {"is_active": "yes"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_is_active",
        )

    def test_default_page_size_comes_from_system_settings(self):
        self.login_as(self.admin)

        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)

        response = self.client.get(self.curriculum_list_url())

        self.assertEqual(response.status_code, 200)

        data = response.json()

        self.assertEqual(data["count"], 4)
        self.assertEqual(data["page_size"], 1)
        self.assertEqual(len(data["curriculums"]), 1)
        self.assertEqual(data["total_pages"], 4)

    def test_max_page_size_comes_from_system_settings(self):
        self.login_as(self.admin)

        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)

        response = self.client.get(
            self.curriculum_list_url(),
            {"page_size": 3},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_page_size",
        )

    def test_invalid_page_size_returns_400(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_list_url(),
            {"page_size": "101"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_page_size",
        )

    def test_admin_searches_curriculums(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_list_url(),
            {"search": "برنامه‌نویسی"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        self.assertEqual(
            response.json()["curriculums"][0]["id"],
            self.student_curriculum.curriculum_id,
        )

    # =========================================================
    # Admin detail tests
    # =========================================================

    def test_admin_can_view_inactive_curriculum_detail(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.curriculum_detail_url(self.inactive_curriculum)
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["curriculum"]["id"],
            self.inactive_curriculum.curriculum_id,
        )
        self.assertFalse(
            response.json()["curriculum"]["is_active"]
        )

    def test_nonexistent_curriculum_detail_returns_404(self):
        self.login_as(self.admin)

        response = self.client.get(
            reverse(
                "curriculum:curriculum-detail",
                kwargs={"curriculum_id": 999999},
            )
        )

        self.assertEqual(response.status_code, 404)

    # =========================================================
    # Admin create tests
    # =========================================================

    def test_admin_can_create_curriculum(self):
        self.login_as(self.admin)

        new_lesson = Lesson.objects.create(
            lesson_code="CUR-301",
            title="درس جدید آزمون",
            theory_units=3,
            practical_units=0,
            department=self.department,
        )

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": self.field.pk,
                "lesson_id": new_lesson.pk,
                "requirement_type_id": self.requirement_type.pk,
                "recommended_term": 4,
                "calculated_units": 3,
            },
        )

        self.assertEqual(response.status_code, 201)

        created = Curriculum.objects.get(
            field=self.field,
            lesson=new_lesson,
        )

        self.assertEqual(
            response.json()["curriculum"]["id"],
            created.curriculum_id,
        )
        self.assertTrue(created.is_active)
        self.assertEqual(created.recommended_term, 4)
        self.assertEqual(created.calculated_units, 3)

    def test_admin_cannot_create_duplicate_curriculum(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": self.field.pk,
                "lesson_id": self.lesson.pk,
                "recommended_term": 1,
                "calculated_units": 3,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["error"]["code"],
            "duplicate_curriculum",
        )

    def test_create_with_inactive_field_returns_404(self):
        self.login_as(self.admin)

        inactive_field = Field.objects.create(
            department=self.department,
            field_name="رشته غیرفعال آزمون",
            field_code="CUR-FIELD-INACTIVE",
            is_active=False,
        )

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": inactive_field.pk,
                "lesson_id": self.lesson.pk,
                "recommended_term": 1,
                "calculated_units": 3,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "field_not_found",
        )

    def test_create_with_wrong_requirement_type_category_returns_404(self):
        self.login_as(self.admin)

        wrong_constant = Constant.objects.create(
            category="academic_rank",
            code="CUR-WRONG-CATEGORY",
            label="مقدار نامعتبر",
        )

        new_lesson = Lesson.objects.create(
            lesson_code="CUR-302",
            title="درس دیگر آزمون",
            theory_units=2,
            practical_units=0,
            department=self.department,
        )

        response = self.json_post(
            self.curriculum_create_url(),
            {
                "field_id": self.field.pk,
                "lesson_id": new_lesson.pk,
                "requirement_type_id": wrong_constant.pk,
                "recommended_term": 1,
                "calculated_units": 2,
            },
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "requirement_type_not_found",
        )

    # =========================================================
    # Admin update tests
    # =========================================================

    def test_admin_can_patch_curriculum(self):
        self.login_as(self.admin)

        response = self.client.patch(
            self.curriculum_update_url(self.student_curriculum),
            data=json.dumps({"recommended_term": 5}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.student_curriculum.refresh_from_db()

        self.assertEqual(self.student_curriculum.recommended_term, 5)
        self.assertEqual(self.student_curriculum.calculated_units, 3)

    def test_admin_can_put_curriculum(self):
        self.login_as(self.admin)

        response = self.client.put(
            self.curriculum_update_url(self.student_curriculum),
            data=json.dumps({
                "field_id": self.field.pk,
                "lesson_id": self.lesson.pk,
                "requirement_type_id": self.requirement_type.pk,
                "recommended_term": 6,
                "calculated_units": 3,
                "is_active": True,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

        self.student_curriculum.refresh_from_db()

        self.assertEqual(self.student_curriculum.recommended_term, 6)

    def test_put_without_required_fields_returns_400(self):
        self.login_as(self.admin)

        response = self.client.put(
            self.curriculum_update_url(self.student_curriculum),
            data=json.dumps({"recommended_term": 6}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "missing_field",
        )

    def test_update_unknown_field_returns_400(self):
        self.login_as(self.admin)

        response = self.client.patch(
            self.curriculum_update_url(self.student_curriculum),
            data=json.dumps({"unknown_field": "value"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "unknown_fields",
        )

    # =========================================================
    # Admin activate / deactivate tests
    # =========================================================

    def test_admin_can_deactivate_curriculum(self):
        self.login_as(self.admin)

        response = self.client.post(
            self.curriculum_deactivate_url(self.student_curriculum)
        )

        self.assertEqual(response.status_code, 200)

        self.student_curriculum.refresh_from_db()
        self.assertFalse(self.student_curriculum.is_active)

        self.assertFalse(
            response.json()["curriculum"]["is_active"]
        )

    def test_admin_can_activate_curriculum(self):
        self.login_as(self.admin)

        response = self.client.post(
            self.curriculum_activate_url(self.inactive_curriculum)
        )

        self.assertEqual(response.status_code, 200)

        self.inactive_curriculum.refresh_from_db()
        self.assertTrue(self.inactive_curriculum.is_active)

        self.assertTrue(
            response.json()["curriculum"]["is_active"]
        )

    def test_student_cannot_activate_curriculum(self):
        self.login_as(self.student_person)

        response = self.client.post(
            self.curriculum_activate_url(self.inactive_curriculum)
        )

        self.assertEqual(response.status_code, 403)

        self.inactive_curriculum.refresh_from_db()
        self.assertFalse(self.inactive_curriculum.is_active)

    def test_admin_activate_nonexistent_curriculum_returns_404(self):
        self.login_as(self.admin)

        response = self.client.post(
            reverse(
                "curriculum:curriculum-activate",
                kwargs={"curriculum_id": 999999},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_curriculum_has_no_delete_endpoint(self):
        self.login_as(self.admin)

        response = self.client.delete(
            self.curriculum_detail_url(self.student_curriculum)
        )

        self.assertEqual(response.status_code, 405)

        self.assertTrue(
            Curriculum.objects.filter(
                pk=self.student_curriculum.pk
            ).exists()
        )

from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import (
    Constant,
    Department,
    Faculty,
    Field,
    Person,
    Student,
    SystemSetting,
    Teacher,
)


class PeopleAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Constants
        cls.bachelor = Constant.objects.create(
            category="educational_level",
            code="bachelor",
            label="کارشناسی",
        )
        cls.master = Constant.objects.create(
            category="educational_level",
            code="master",
            label="کارشناسی ارشد",
        )
        cls.active = Constant.objects.create(
            category="student_status",
            code="active",
            label="فعال",
        )
        cls.probation = Constant.objects.create(
            category="student_status",
            code="probation",
            label="مشروط",
        )

        # Faculty, departments and fields
        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده آزمون People",
            faculty_code="PPL-FAC",
        )

        cls.computer_department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه کامپیوتر آزمون",
            department_code="PPL-CS",
        )

        cls.math_department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه ریاضی آزمون",
            department_code="PPL-MATH",
        )

        cls.computer_field = Field.objects.create(
            department=cls.computer_department,
            field_name="مهندسی کامپیوتر آزمون",
            field_code="PPL-COMP",
        )

        cls.math_field = Field.objects.create(
            department=cls.math_department,
            field_name="ریاضی آزمون",
            field_code="PPL-MAT",
        )

        # Admin user
        cls.admin = Person.objects.create_user(
            username="people-api-admin",
            password="TestPassword@123",
            first_name="مدیر",
            last_name="آزمون",
            email="people-admin@example.com",
            national_id="9910000001",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
            is_staff=True,
            is_superuser=True,
        )

        # Student users
        cls.student_persons = [
            Person.objects.create_user(
                username="people-sara-1",
                password="TestPassword@123",
                first_name="سارا",
                last_name="احمدی",
                email="sara1@example.com",
                national_id="9910000002",
                birth_date=date(2002, 1, 1),
                birth_place="تهران",
            ),
            Person.objects.create_user(
                username="people-ali-1",
                password="TestPassword@123",
                first_name="علی",
                last_name="کریمی",
                email="ali1@example.com",
                national_id="9910000003",
                birth_date=date(2001, 2, 2),
                birth_place="تهران",
            ),
            Person.objects.create_user(
                username="people-sara-2",
                password="TestPassword@123",
                first_name="سارا",
                last_name="محمدی",
                email="sara2@example.com",
                national_id="9910000004",
                birth_date=date(2003, 3, 3),
                birth_place="تهران",
            ),
        ]

        # Student records
        cls.students = [
            Student.objects.create(
                person=cls.student_persons[0],
                student_code="PPL-001",
                educational_level=cls.bachelor,
                field=cls.computer_field,
                application_date=date(2022, 9, 23),
                status=cls.active,
                total_gpa=Decimal("17.50"),
            ),
            Student.objects.create(
                person=cls.student_persons[1],
                student_code="PPL-002",
                educational_level=cls.master,
                field=cls.math_field,
                application_date=date(2023, 9, 23),
                status=cls.probation,
                total_gpa=Decimal("11.50"),
            ),
            Student.objects.create(
                person=cls.student_persons[2],
                student_code="PPL-003",
                educational_level=cls.bachelor,
                field=cls.computer_field,
                application_date=date(2024, 9, 23),
                status=cls.active,
                total_gpa=Decimal("16.00"),
            ),
        ]

        # Academic ranks for teacher API tests
        cls.assistant_professor = Constant.objects.create(
            category="academic_rank",
            code="assistant_professor",
            label="استادیار",
        )

        cls.associate_professor = Constant.objects.create(
            category="academic_rank",
            code="associate_professor",
            label="دانشیار",
        )

        # Teacher users
        cls.teacher_persons = [
            Person.objects.create_user(
                username="people-teacher-1",
                password="TestPassword@123",
                first_name="مریم",
                last_name="رضایی",
                email="teacher1@example.com",
                national_id="9910000011",
                birth_date=date(1985, 4, 4),
                birth_place="شهر آزمون یک",
            ),
            Person.objects.create_user(
                username="people-teacher-2",
                password="TestPassword@123",
                first_name="رضا",
                last_name="حسینی",
                email="teacher2@example.com",
                national_id="9910000012",
                birth_date=date(1982, 5, 5),
                birth_place="شهر آزمون دو",
            ),
            Person.objects.create_user(
                username="people-teacher-3",
                password="TestPassword@123",
                first_name="نگار",
                last_name="محمدی",
                email="teacher3@example.com",
                national_id="9910000013",
                birth_date=date(1988, 6, 6),
                birth_place="شهر آزمون سه",
            ),
        ]

        # Teacher records
        cls.teachers = [
            Teacher.objects.create(
                person=cls.teacher_persons[0],
                teacher_code="PPL-T-001",
                department=cls.computer_department,
                academic_rank=cls.assistant_professor,
                hire_date=date(2015, 9, 1),
            ),
            Teacher.objects.create(
                person=cls.teacher_persons[1],
                teacher_code="PPL-T-002",
                department=cls.math_department,
                academic_rank=cls.associate_professor,
                hire_date=date(2010, 9, 1),
            ),
            Teacher.objects.create(
                person=cls.teacher_persons[2],
                teacher_code="PPL-T-003",
                department=cls.computer_department,
                academic_rank=None,
                hire_date=date(2020, 9, 1),
            ),
        ]

    def setUp(self):
        self.list_url = "/api/people/students/"

    def login_as_admin(self):
        self.client.force_login(self.admin)

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

    def test_students_default_page_size_comes_from_system_settings(self):
        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.login_as_admin()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["pagination"]["page_size"], 1)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["pagination"]["total_pages"], 3)

    def test_students_max_page_size_comes_from_system_settings(self):
        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page_size": 3},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_pagination",
        )

    def test_teachers_default_page_size_comes_from_system_settings(self):
        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.login_as_admin()

        response = self.client.get("/api/people/teachers/")

        self.assertEqual(response.status_code, 200)

        payload = response.json()
        self.assertEqual(payload["pagination"]["page_size"], 1)
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["pagination"]["total_pages"], 3)

    def test_teachers_max_page_size_comes_from_system_settings(self):
        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page_size": 3},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_pagination",
        )

    # ------------------------------------------
    # Authentication and authorization
    # ------------------------------------------

    def test_anonymous_user_cannot_access_students_list(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, 401)

    def test_student_cannot_access_admin_students_list(self):
        self.client.force_login(self.student_persons[0])

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_students_list(self):
        self.login_as_admin()

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["count"], 3)

    # ------------------------------------------
    # Search
    # ------------------------------------------

    def test_search_matches_first_name(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"search": "سارا"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 2)

    def test_search_matches_last_name(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"search": "کریمی"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.json()["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_code"], "PPL-002")

    def test_search_matches_student_code(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"search": "PPL-002"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["results"][0]["student_code"],
            "PPL-002",
        )

    def test_student_code_filter_is_exact(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"student_code": "PPL-001"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    # ------------------------------------------
    # Filters
    # ------------------------------------------

    def test_educational_level_filter(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"educational_level": "master"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)
        self.assertEqual(
            response.json()["results"][0]["student_code"],
            "PPL-002",
        )

    def test_status_filter(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"status": "probation"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_field_filter(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"field": "PPL-COMP"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 2)

    def test_department_filter(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"department": "PPL-MATH"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_filters_can_be_combined(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {
                "educational_level": "bachelor",
                "status": "active",
                "field": "PPL-COMP",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 2)

    # ------------------------------------------
    # Pagination
    # ------------------------------------------

    def test_pagination_returns_correct_metadata(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page": 2, "page_size": 1},
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["pagination"]["page"], 2)
        self.assertEqual(payload["pagination"]["page_size"], 1)
        self.assertEqual(payload["pagination"]["total_pages"], 3)
        self.assertTrue(payload["pagination"]["has_next"])
        self.assertTrue(payload["pagination"]["has_previous"])

    def test_invalid_page_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page": "abc"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_pagination",
        )

    def test_page_zero_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page": 0},
        )

        self.assertEqual(response.status_code, 400)

    def test_page_size_over_100_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page_size": 101},
        )

        self.assertEqual(response.status_code, 400)

    def test_page_size_zero_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page_size": 0},
        )

        self.assertEqual(response.status_code, 400)

    def test_nonexistent_page_returns_404(self):
        self.login_as_admin()

        response = self.client.get(
            self.list_url,
            {"page": 99, "page_size": 1},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "page_not_found",
        )

    # ------------------------------------------
    # Student detail
    # ------------------------------------------

    def test_admin_can_retrieve_student_detail(self):
        self.login_as_admin()

        response = self.client.get(
            f"/api/people/students/{self.students[0].pk}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["student"]["student_code"],
            "PPL-001",
        )

    def test_unknown_student_detail_returns_404(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/students/999999/"
        )

        self.assertEqual(response.status_code, 404)

    # ------------------------------------------
    # Teacher API authentication and authorization
    # ------------------------------------------

    def test_anonymous_user_cannot_access_teacher_profile(self):
        response = self.client.get("/api/people/teachers/me/")
        self.assertEqual(response.status_code, 401)

    def test_student_cannot_access_teacher_profile(self):
        self.client.force_login(self.student_persons[0])

        response = self.client.get("/api/people/teachers/me/")

        self.assertEqual(response.status_code, 403)

    def test_professor_can_access_own_teacher_profile(self):
        self.client.force_login(self.teacher_persons[0])

        response = self.client.get("/api/people/teachers/me/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["teacher"]["teacher_code"],
            "PPL-T-001",
        )
        self.assertEqual(
            payload["teacher"]["person"]["username"],
            "people-teacher-1",
        )

    def test_anonymous_user_cannot_access_teachers_list(self):
        response = self.client.get("/api/people/teachers/")
        self.assertEqual(response.status_code, 401)

    def test_student_cannot_access_teachers_list(self):
        self.client.force_login(self.student_persons[0])

        response = self.client.get("/api/people/teachers/")

        self.assertEqual(response.status_code, 403)

    def test_professor_cannot_access_admin_teachers_list(self):
        self.client.force_login(self.teacher_persons[0])

        response = self.client.get("/api/people/teachers/")

        self.assertEqual(response.status_code, 403)

    def test_admin_can_access_teachers_list(self):
        self.login_as_admin()

        response = self.client.get("/api/people/teachers/")

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["count"], 3)

    # ------------------------------------------
    # Teacher search
    # ------------------------------------------

    def test_teacher_search_matches_first_name(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"search": "مریم"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_search_matches_last_name(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"search": "حسینی"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_search_matches_username(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"search": "people-teacher-2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_search_matches_email(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"search": "teacher3@example.com"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_search_matches_teacher_code(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"search": "PPL-T-002"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    # ------------------------------------------
    # Teacher filters
    # ------------------------------------------

    def test_teacher_code_filter_is_exact(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"teacher_code": "PPL-T-001"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_department_filter_by_code(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"department": "PPL-MATH"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_department_filter_by_id(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"department": str(self.computer_department.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 2)

    def test_teacher_department_filter_by_name(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"department": "گروه ریاضی"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_academic_rank_filter_by_code(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"academic_rank": "assistant_professor"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_academic_rank_filter_by_label(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"academic_rank": "دانشیار"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_academic_rank_filter_by_id(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"academic_rank": str(self.assistant_professor.pk)},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    def test_teacher_filters_can_be_combined(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {
                "department": "PPL-CS",
                "academic_rank": "assistant_professor",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["total_count"], 1)

    # ------------------------------------------
    # Teacher pagination
    # ------------------------------------------

    def test_teacher_pagination_returns_correct_metadata(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page": 2, "page_size": 1},
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["total_count"], 3)
        self.assertEqual(payload["pagination"]["page"], 2)
        self.assertEqual(payload["pagination"]["page_size"], 1)
        self.assertEqual(payload["pagination"]["total_pages"], 3)
        self.assertTrue(payload["pagination"]["has_next"])
        self.assertTrue(payload["pagination"]["has_previous"])

    def test_teacher_invalid_page_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page": "abc"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_pagination",
        )

    def test_teacher_page_zero_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page": 0},
        )

        self.assertEqual(response.status_code, 400)

    def test_teacher_page_size_over_100_returns_400(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page_size": 101},
        )

        self.assertEqual(response.status_code, 400)

    def test_teacher_nonexistent_page_returns_404(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/",
            {"page": 99, "page_size": 1},
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "page_not_found",
        )

    # ------------------------------------------
    # Teacher detail and data protection
    # ------------------------------------------

    def test_admin_can_retrieve_teacher_detail(self):
        self.login_as_admin()

        response = self.client.get(
            f"/api/people/teachers/{self.teachers[0].pk}/"
        )

        self.assertEqual(response.status_code, 200)

        payload = response.json()

        self.assertTrue(payload["success"])
        self.assertEqual(
            payload["teacher"]["teacher_code"],
            "PPL-T-001",
        )

    def test_unknown_teacher_detail_returns_404(self):
        self.login_as_admin()

        response = self.client.get(
            "/api/people/teachers/999999/"
        )

        self.assertEqual(response.status_code, 404)

    def test_professor_cannot_access_admin_teacher_detail(self):
        self.client.force_login(self.teacher_persons[0])

        response = self.client.get(
            f"/api/people/teachers/{self.teachers[0].pk}/"
        )

        self.assertEqual(response.status_code, 403)

    def test_teacher_api_does_not_expose_sensitive_personal_data(self):
        self.login_as_admin()

        response = self.client.get(
            f"/api/people/teachers/{self.teachers[0].pk}/"
        )

        self.assertEqual(response.status_code, 200)

        person_payload = response.json()["teacher"]["person"]

        self.assertNotIn("national_id", person_payload)
        self.assertNotIn("password", person_payload)
        self.assertNotIn("address", person_payload)
        self.assertNotIn("birth_date", person_payload)

    def test_teacher_without_academic_rank_returns_null_rank(self):
        self.login_as_admin()

        response = self.client.get(
            f"/api/people/teachers/{self.teachers[2].pk}/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIsNone(
            response.json()["teacher"]["academic_rank"]
        )


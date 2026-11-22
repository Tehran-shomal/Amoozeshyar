import importlib
import json
from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone

from apps.core import api
from apps.core.models import (
    Classroom,
    Constant,
    CourseOffering,
    Department,
    Enrollment,
    Faculty,
    Field,
    Grade,
    Lesson,
    Person,
    Prerequisite,
    Role,
    Student,
    SystemSetting,
    Teacher,
    Term,
    UserAccount,
)


# FUFP01, FUFP02, FUFP03, FUFD01, FUFP04, FUD01, FUFD07, FUFD08, FUFD09,
# #132 NFRP01, and #133 NFRP02.
class EnrollmentFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()
        cls.constants = {}
        constant_values = (
            ("enrollment_status", "registered", "ثبت‌نام‌شده"),
            ("enrollment_status", "dropped", "حذف‌شده"),
            ("student_status", "active", "فعال"),
            ("student_status", "probation", "مشروط"),
            ("student_status", "on_leave", "مرخصی"),
            ("day_of_week", "saturday", "شنبه"),
            ("day_of_week", "sunday", "یکشنبه"),
            ("day_of_week", "monday", "دوشنبه"),
            ("day_of_week", "tuesday", "سه‌شنبه"),
            ("day_of_week", "wednesday", "چهارشنبه"),
            ("day_of_week", "thursday", "پنجشنبه"),
            ("day_of_week", "friday", "جمعه"),
            ("semester", "mehr", "مهر"),
            ("educational_level", "bachelor", "کارشناسی"),
            ("prerequisite_type", "prerequisite", "پیش‌نیاز"),
            ("prerequisite_type", "co_requisite", "هم‌نیاز"),
        )
        for category, code, label in constant_values:
            cls.constants[(category, code)] = Constant.objects.get_or_create(
                category=category,
                code=code,
                defaults={"label": label},
            )[0]

        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده آزمون",
            faculty_code="TST",
        )
        cls.department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه آزمون",
            department_code="TST",
        )
        cls.field = Field.objects.create(
            department=cls.department,
            field_name="رشته آزمون",
            field_code="TST",
        )
        cls.person = cls.create_person("student", "0011111111")
        cls.student = Student.objects.create(
            person=cls.person,
            student_code="S-001",
            educational_level=cls.constants[("educational_level", "bachelor")],
            field=cls.field,
            application_date=date(2022, 9, 23),
            status=cls.constants[("student_status", "active")],
            previous_term_gpa=Decimal("16.00"),
        )
        cls.student_role = Role.objects.create(role_name="دانشجو")
        UserAccount.objects.create(
            person=cls.person,
            role=cls.student_role,
            username="student-account",
            password="not-used-by-authentication",
        )

        cls.term = Term.objects.create(
            term_code="T-14051",
            semester=cls.constants[("semester", "mehr")],
            academic_year="1405-1406",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=150),
            registration_start=cls.now - timedelta(days=1),
            registration_end=cls.now + timedelta(days=1),
            add_drop_start=cls.now + timedelta(days=2),
            add_drop_end=cls.now + timedelta(days=3),
            emergency_drop_start=cls.now + timedelta(days=4),
            emergency_drop_end=cls.now + timedelta(days=5),
            is_active=True,
        )

    @classmethod
    def create_person(cls, username, national_id):
        return Person.objects.create_user(
            username=username,
            password="Person@Password1",
            first_name=username,
            last_name="آزمون",
            email=f"{username}@example.com",
            national_id=national_id,
            birth_date=date(2001, 1, 1),
            birth_place="تهران",
        )

    def setUp(self):
        self.counter = 0

    def constant(self, category, code):
        return self.constants[(category, code)]

    def create_student(self, code, national_id, **overrides):
        person = self.create_person(code.lower(), national_id)
        values = {
            "person": person,
            "student_code": code,
            "educational_level": self.constant("educational_level", "bachelor"),
            "field": self.field,
            "application_date": date(2022, 9, 23),
            "status": self.constant("student_status", "active"),
            "previous_term_gpa": Decimal("16.00"),
            "tuition_debt": Decimal("0"),
        }
        values.update(overrides)
        return Student.objects.create(**values)

    def create_offering(
        self,
        *,
        day="saturday",
        start=time(8, 0),
        end=time(10, 0),
        capacity=20,
        exam_date=None,
        exam_time=None,
        term=None,
        lesson_units=3,
    ):
        self.counter += 1
        lesson = Lesson.objects.create(
            lesson_code=f"L-{self.counter:03}",
            title=f"درس آزمون {self.counter}",
            theory_units=lesson_units,
            practical_units=0,
            department=self.department,
        )
        teacher_person = self.create_person(
            f"teacher-{self.counter}",
            f"002{self.counter:07}",
        )
        teacher = Teacher.objects.create(
            person=teacher_person,
            teacher_code=f"T-{self.counter:03}",
            department=self.department,
            hire_date=date(2015, 9, 1),
        )
        room = Classroom.objects.create(
            building_name="ساختمان آزمون",
            room_number=f"{self.counter:03}",
            capacity=40,
            classroom_type="کلاس",
        )
        return CourseOffering.objects.create(
            lesson=lesson,
            term=term or self.term,
            teacher=teacher,
            capacity=capacity,
            day_of_week=self.constant("day_of_week", day),
            start_time=start,
            end_time=end,
            classroom=room,
            exam_date=exam_date,
            exam_time=exam_time,
            is_active=True,
        )

    def make_enrollment(self, student, offering, status_code="registered"):
        return Enrollment.objects.create(
            student=student,
            offering=offering,
            status=self.constant("enrollment_status", status_code),
        )

    def enrollment_service(self):
        try:
            return importlib.import_module("apps.core.enrollment.services")
        except ModuleNotFoundError:
            self.fail("apps.core.enrollment.services is not implemented")


class EnrollmentServiceTests(EnrollmentFixtures):
    def register(self, student=None, offering=None, now=None):
        service = self.enrollment_service()
        register_student = getattr(service, "register_student", None)
        self.assertTrue(callable(register_student), "register_student is not implemented")
        return register_student(
            student or self.student,
            (offering or self.create_offering()).pk,
            now=now or self.now,
        )

    def test_registration_succeeds_and_sets_registered_status(self):
        enrollment = self.register()

        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.status.code, "registered")

    def test_registration_is_idempotent_for_an_existing_active_enrollment(self):
        offering = self.create_offering(capacity=1)
        existing = self.make_enrollment(self.student, offering)
        self.term.registration_end = self.now - timedelta(hours=1)
        self.term.save(update_fields=["registration_end"])
        self.student.tuition_debt = Decimal("500")
        self.student.save(update_fields=["tuition_debt"])

        returned = self.register(offering=offering)

        self.assertEqual(returned.pk, existing.pk)
        self.assertEqual(Enrollment.objects.filter(student=self.student).count(), 1)

    def test_registration_treats_a_legacy_null_status_as_active(self):
        offering = self.create_offering(capacity=1)
        existing = Enrollment.objects.create(student=self.student, offering=offering)

        returned = self.register(offering=offering)

        self.assertEqual(returned.pk, existing.pk)
        self.assertIsNone(returned.status)

    def test_dropped_enrollment_is_reactivated_inside_registration_window(self):
        offering = self.create_offering()
        existing = self.make_enrollment(self.student, offering, "dropped")
        existing.drop_date = date.today() - timedelta(days=1)
        existing.save(update_fields=["drop_date"])

        returned = self.register(offering=offering)
        returned.refresh_from_db()

        self.assertEqual(returned.pk, existing.pk)
        self.assertEqual(returned.status.code, "registered")
        self.assertIsNone(returned.drop_date)

    def test_registration_rejects_inactive_terms_and_offerings(self):
        offering = self.create_offering()
        self.term.is_active = False
        self.term.save(update_fields=["is_active"])
        with self.assertRaises(api.APIError) as inactive_term:
            self.register(offering=offering)
        self.assertEqual(inactive_term.exception.code, "term_not_active")

        self.term.is_active = True
        self.term.save(update_fields=["is_active"])
        offering.is_active = False
        offering.save(update_fields=["is_active"])
        with self.assertRaises(api.APIError) as inactive_offering:
            self.register(offering=offering)
        self.assertEqual(inactive_offering.exception.code, "inactive_offering")

    def test_registration_rejects_closed_registration_and_add_drop_windows(self):
        self.term.registration_start = self.now - timedelta(days=3)
        self.term.registration_end = self.now - timedelta(days=2)
        self.term.add_drop_start = self.now + timedelta(days=1)
        self.term.add_drop_end = self.now + timedelta(days=2)
        self.term.save()

        with self.assertRaises(api.APIError) as raised:
            self.register()

        self.assertEqual(raised.exception.code, "registration_window_closed")

    def test_registration_rejects_students_with_tuition_debt(self):
        self.student.tuition_debt = Decimal("1")
        self.student.save(update_fields=["tuition_debt"])

        with self.assertRaises(api.APIError) as raised:
            self.register()

        self.assertEqual(raised.exception.code, "tuition_debt")

    def test_registration_rejects_students_who_are_not_active(self):
        self.student.status = self.constant("student_status", "on_leave")
        self.student.save(update_fields=["status"])

        with self.assertRaises(api.APIError) as raised:
            self.register()

        self.assertEqual(raised.exception.code, "student_not_eligible")

    def test_probation_students_can_register_with_their_reduced_credit_limit(self):
        probation = self.constant("student_status", "probation")
        self.student.status = probation
        self.student.previous_term_gpa = Decimal("9.00")
        self.student.save(update_fields=["status", "previous_term_gpa"])
        offering = self.create_offering(lesson_units=3)

        enrollment = self.register(offering=offering)

        self.assertEqual(enrollment.status.code, "registered")

    def test_probation_status_caps_load_even_when_previous_gpa_is_high(self):
        self.student.status = self.constant("student_status", "probation")
        self.student.previous_term_gpa = Decimal("18.00")
        self.student.save(update_fields=["status", "previous_term_gpa"])
        existing = self.create_offering(lesson_units=11, day="saturday")
        self.make_enrollment(self.student, existing)
        target = self.create_offering(lesson_units=4, day="sunday")

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=target)

        self.assertEqual(raised.exception.code, "credit_limit_exceeded")

    def test_legacy_suspended_code_with_probation_label_uses_probation_rules(self):
        legacy_status = Constant.objects.create(
            category="student_status", code="suspended", label="مشروط"
        )
        self.student.status = legacy_status
        self.student.previous_term_gpa = Decimal("18.00")
        self.student.save(update_fields=["status", "previous_term_gpa"])
        existing = self.create_offering(lesson_units=11, day="saturday")
        self.make_enrollment(self.student, existing)
        target = self.create_offering(lesson_units=4, day="sunday")

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=target)

        self.assertEqual(raised.exception.code, "credit_limit_exceeded")

    def test_register_endpoint_accepts_student_code_for_multiple_profiles(self):
        master = Constant.objects.create(
            category="educational_level", code="master", label="Master"
        )
        Student.objects.create(
            person=self.person,
            student_code="S-002",
            educational_level=master,
            field=self.field,
            application_date=date(2023, 9, 23),
            status=self.constant("student_status", "active"),
        )
        offering = self.create_offering()
        self.client.force_login(self.person)

        ambiguous = self.client.post(f"/api/enrollment/register/{offering.pk}/")
        registered = self.client.post(
            f"/api/enrollment/register/{offering.pk}/",
            data=json.dumps({"student_code": "S-002"}),
            content_type="application/json",
        )

        self.assertEqual(ambiguous.status_code, 400)
        self.assertEqual(ambiguous.json()["error"]["code"], "student_profile_ambiguous")
        self.assertEqual(registered.status_code, 201)
        self.assertEqual(registered.json()["enrollment"]["student_code"], "S-002")

        now = timezone.now()
        self.term.add_drop_start = now - timedelta(hours=1)
        self.term.add_drop_end = now + timedelta(hours=1)
        self.term.save(update_fields=["add_drop_start", "add_drop_end"])
        dropped = self.client.post(
            f"/api/enrollment/drop/{registered.json()['enrollment']['id']}/",
            data=json.dumps({"student_code": "S-002"}),
            content_type="application/json",
        )
        self.assertEqual(dropped.status_code, 200)
        self.assertEqual(dropped.json()["enrollment"]["student_code"], "S-002")
        self.assertEqual(dropped.json()["enrollment"]["status"], "dropped")

    def test_repeated_registration_returns_ok_instead_of_created(self):
        offering = self.create_offering()
        self.client.force_login(self.person)

        first = self.client.post(f"/api/enrollment/register/{offering.pk}/")
        repeated = self.client.post(f"/api/enrollment/register/{offering.pk}/")

        self.assertEqual(first.status_code, 201)
        self.assertEqual(repeated.status_code, 200)

    def test_registration_requires_a_passing_prerequisite_grade(self):
        offering = self.create_offering()
        prerequisite_offering = self.create_offering(
            term=self.create_past_term(),
            day="monday",
        )
        Prerequisite.objects.create(
            lesson=offering.lesson,
            prerequisite_lesson=prerequisite_offering.lesson,
            prerequisite_type=self.constant("prerequisite_type", "prerequisite"),
        )
        prior_enrollment = self.make_enrollment(
            self.student,
            prerequisite_offering,
        )
        Grade.objects.create(enrollment=prior_enrollment, score=Decimal("9.99"))

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=offering)

        self.assertEqual(raised.exception.code, "prerequisite_not_met")

    def test_a_grade_of_ten_satisfies_a_prerequisite(self):
        offering = self.create_offering()
        prerequisite_offering = self.create_offering(
            term=self.create_past_term(),
            day="monday",
        )
        Prerequisite.objects.create(
            lesson=offering.lesson,
            prerequisite_lesson=prerequisite_offering.lesson,
            prerequisite_type=self.constant("prerequisite_type", "prerequisite"),
        )
        prior_enrollment = self.make_enrollment(self.student, prerequisite_offering)
        Grade.objects.create(enrollment=prior_enrollment, score=Decimal("10.00"))

        enrollment = self.register(offering=offering)

        self.assertEqual(enrollment.status.code, "registered")

    def test_custom_minimum_passing_grade_is_read_from_system_settings(self):
        decimal_type, _ = Constant.objects.get_or_create(
            category="data_type",
            code="decimal",
            defaults={"label": "عدد اعشاری"},
        )

        SystemSetting.objects.update_or_create(
            setting_key="minimum_passing_grade",
            defaults={
                "setting_value": "10.5",
                "data_type": decimal_type,
            },
        )

        offering = self.create_offering()
        prerequisite_offering = self.create_offering(
            term=self.create_past_term(),
            day="monday",
        )

        Prerequisite.objects.create(
            lesson=offering.lesson,
            prerequisite_lesson=prerequisite_offering.lesson,
            prerequisite_type=self.constant("prerequisite_type", "prerequisite"),
        )

        prior_enrollment = self.make_enrollment(
            self.student,
            prerequisite_offering,
        )
        grade = Grade.objects.create(
            enrollment=prior_enrollment,
            score=Decimal("10.00"),
        )

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=offering)

        self.assertEqual(raised.exception.code, "prerequisite_not_met")

        grade.score = Decimal("10.50")
        grade.save(update_fields=["score"])

        enrollment = self.register(offering=offering)

        self.assertEqual(enrollment.status.code, "registered")

    def test_co_requisite_requires_a_same_term_registration(self):
        offering = self.create_offering()
        co_requisite = self.create_offering(day="monday")
        Prerequisite.objects.create(
            lesson=offering.lesson,
            prerequisite_lesson=co_requisite.lesson,
            prerequisite_type=self.constant("prerequisite_type", "co_requisite"),
        )
        service = self.enrollment_service()

        with self.assertRaises(api.APIError) as raised:
            service.register_student(self.student, offering.pk, now=self.now)
        self.assertEqual(raised.exception.code, "corequisite_not_met")

        self.make_enrollment(self.student, co_requisite)
        enrollment = service.register_student(self.student, offering.pk, now=self.now)
        self.assertEqual(enrollment.status.code, "registered")

    def test_registration_rejects_overlapping_weekly_schedules(self):
        existing_offering = self.create_offering(
            day="saturday",
            start=time(9, 0),
            end=time(11, 0),
        )
        self.make_enrollment(self.student, existing_offering)
        target = self.create_offering(
            day="saturday",
            start=time(10, 0),
            end=time(12, 0),
        )

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=target)

        self.assertEqual(raised.exception.code, "schedule_conflict")

    def test_registration_rejects_same_day_same_time_exams(self):
        exam_date = date.today() + timedelta(days=60)
        existing_offering = self.create_offering(
            day="saturday",
            exam_date=exam_date,
            exam_time=time(9, 0),
        )
        self.make_enrollment(self.student, existing_offering)
        target = self.create_offering(
            day="monday",
            exam_date=exam_date,
            exam_time=time(9, 0),
        )

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=target)

        self.assertEqual(raised.exception.code, "exam_conflict")

    def test_registration_rejects_credit_limit_overflow(self):
        self.student.previous_term_gpa = Decimal("11.00")
        self.student.save(update_fields=["previous_term_gpa"])
        for index, day in enumerate(("saturday", "sunday", "monday", "tuesday")):
            offering = self.create_offering(
                day=day,
                start=time(7 + index * 2, 0),
                end=time(8 + index * 2, 0),
            )
            self.make_enrollment(self.student, offering)
        target = self.create_offering(day="wednesday")

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=target)

        self.assertEqual(raised.exception.code, "credit_limit_exceeded")

    def test_registration_rejects_a_full_offering(self):
        offering = self.create_offering(capacity=1)
        another_student = self.create_student("S-002", "0011111112")
        self.make_enrollment(another_student, offering)

        with self.assertRaises(api.APIError) as raised:
            self.register(offering=offering)

        self.assertEqual(raised.exception.code, "offering_full")

    def test_drop_is_allowed_during_add_drop_and_records_the_date(self):
        offering = self.create_offering()
        enrollment = self.make_enrollment(self.student, offering)
        self.term.registration_start = self.now - timedelta(days=3)
        self.term.registration_end = self.now - timedelta(days=2)
        self.term.add_drop_start = self.now - timedelta(hours=1)
        self.term.add_drop_end = self.now + timedelta(hours=1)
        self.term.save()

        dropped = self.enrollment_service().drop_enrollment(
            self.student,
            enrollment.pk,
            now=self.now,
        )
        dropped.refresh_from_db()

        self.assertEqual(dropped.status.code, "dropped")
        self.assertEqual(dropped.drop_date, timezone.localdate(self.now))

    def test_drop_is_allowed_during_emergency_drop(self):
        offering = self.create_offering()
        enrollment = self.make_enrollment(self.student, offering)
        self.term.registration_start = self.now - timedelta(days=5)
        self.term.registration_end = self.now - timedelta(days=4)
        self.term.add_drop_start = self.now - timedelta(days=3)
        self.term.add_drop_end = self.now - timedelta(days=2)
        self.term.emergency_drop_start = self.now - timedelta(hours=1)
        self.term.emergency_drop_end = self.now + timedelta(hours=1)
        self.term.save()

        dropped = self.enrollment_service().drop_enrollment(
            self.student,
            enrollment.pk,
            now=self.now,
        )

        self.assertEqual(dropped.status.code, "dropped")

    def test_drop_rejects_closed_windows_and_other_students_enrollments(self):
        offering = self.create_offering()
        enrollment = self.make_enrollment(self.student, offering)
        self.term.registration_start = self.now - timedelta(days=5)
        self.term.registration_end = self.now - timedelta(days=4)
        self.term.add_drop_start = self.now - timedelta(days=3)
        self.term.add_drop_end = self.now - timedelta(days=2)
        self.term.emergency_drop_start = self.now - timedelta(days=1)
        self.term.emergency_drop_end = self.now - timedelta(hours=1)
        self.term.save()
        service = self.enrollment_service()

        with self.assertRaises(api.APIError) as closed:
            service.drop_enrollment(self.student, enrollment.pk, now=self.now)
        self.assertEqual(closed.exception.code, "drop_window_closed")

        another_student = self.create_student("S-003", "0011111113")
        self.term.add_drop_start = self.now - timedelta(hours=1)
        self.term.add_drop_end = self.now + timedelta(hours=1)
        self.term.save()
        with self.assertRaises(api.APIError) as not_owned:
            service.drop_enrollment(another_student, enrollment.pk, now=self.now)
        self.assertEqual(not_owned.exception.code, "enrollment_not_owned")

    def test_remaining_capacity_counts_lowercase_dropped_rows_as_free(self):
        offering = self.create_offering(capacity=2)
        self.make_enrollment(self.student, offering)
        another_student = self.create_student("S-004", "0011111114")
        self.make_enrollment(another_student, offering, "dropped")

        self.assertEqual(offering.remaining_capacity, 1)

    def create_past_term(self):
        return Term.objects.create(
            term_code=f"P-{self.counter:03}",
            semester=self.constant("semester", "mehr"),
            academic_year=f"{1400 + self.counter:04}-{1401 + self.counter:04}",
            start_date=date.today() - timedelta(days=500),
            end_date=date.today() - timedelta(days=300),
            registration_start=self.now - timedelta(days=600),
            registration_end=self.now - timedelta(days=590),
            add_drop_start=self.now - timedelta(days=580),
            add_drop_end=self.now - timedelta(days=570),
            emergency_drop_start=self.now - timedelta(days=560),
            emergency_drop_end=self.now - timedelta(days=550),
            is_active=False,
        )


class EnrollmentAPITests(EnrollmentFixtures):
    def test_registration_requires_an_authenticated_student(self):
        offering = self.create_offering()

        response = self.client.post(f"/api/enrollment/register/{offering.pk}/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "authentication_required")

    def test_student_can_register_and_drop_through_the_api(self):
        offering = self.create_offering()
        self.assertTrue(self.client.login(username=self.person.username, password="Person@Password1"))

        registered = self.client.post(f"/api/enrollment/register/{offering.pk}/")
        self.assertEqual(registered.status_code, 201)
        enrollment_id = registered.json()["enrollment"]["id"]

        now = timezone.now()
        self.term.add_drop_start = now - timedelta(hours=1)
        self.term.add_drop_end = now + timedelta(hours=1)
        self.term.save(update_fields=["add_drop_start", "add_drop_end"])
        dropped = self.client.post(f"/api/enrollment/drop/{enrollment_id}/")

        self.assertEqual(dropped.status_code, 200)
        self.assertEqual(dropped.json()["enrollment"]["status"], "dropped")

    def test_non_student_role_cannot_use_student_enrollment_api(self):
        person = Person.objects.create_user(
            username="reviewer",
            password="Person@Password1",
            first_name="کارشناس",
            last_name="آموزش",
            email="reviewer@example.com",
            national_id="0099999999",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        self.client.force_login(person)

        response = self.client.post("/api/enrollment/register/1/")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "permission_denied")



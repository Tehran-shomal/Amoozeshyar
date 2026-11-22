import json
from datetime import date, time, timedelta
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import (
    Classroom,
    Constant,
    CourseOffering,
    Department,
    Enrollment,
    Faculty,
    Field,
    Grade,
    GradeAppeal,
    Lesson,
    Person,
    Role,
    Student,
    Teacher,
    TeacherSurvey,
    Term,
    UserAccount,
)


class GradingAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        def constant(category, code, label):
            constant, _ = Constant.objects.get_or_create(
                category=category,
                code=code,
                defaults={"label": label},
            )
            return constant

        enrollment_status = constant(
            "enrollment_status", "registered", "ثبت‌نام‌شده"
        )
        semester = constant("semester", "mehr", "مهر")
        day = constant("day_of_week", "saturday", "شنبه")
        educational_level = constant(
            "educational_level", "bachelor", "کارشناسی"
        )
        student_status = constant("student_status", "active", "فعال")
        cls.appeal_submitted = constant(
            "appeal_status", "submitted", "ثبت‌شده"
        )

        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده تست نمرات",
            faculty_code="GRD",
        )
        cls.department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه تست نمرات",
            department_code="GRD",
        )
        cls.field = Field.objects.create(
            department=cls.department,
            field_name="رشته تست نمرات",
            field_code="GRD",
        )

        cls.student_person = cls.make_person(
            "grading-student", "9811000001"
        )
        cls.professor_person = cls.make_person(
            "grading-professor", "9811000002"
        )

        cls.student = Student.objects.create(
            person=cls.student_person,
            student_code="GRD-S-001",
            educational_level=educational_level,
            field=cls.field,
            application_date=date(2022, 9, 23),
            status=student_status,
        )

        student_role = Role.objects.create(role_name="student")
        professor_role = Role.objects.create(role_name="professor")

        cls.student_account = UserAccount.objects.create(
            person=cls.student_person,
            role=student_role,
            username="grading-student-account",
            password="not-used",
        )
        cls.professor_account = UserAccount.objects.create(
            person=cls.professor_person,
            role=professor_role,
            username="grading-professor-account",
            password="not-used",
        )

        now = timezone.now()
        cls.term = Term.objects.create(
            term_code="GRD-1405",
            semester=semester,
            academic_year="1405-1406",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=150),
            registration_start=now - timedelta(days=10),
            registration_end=now + timedelta(days=10),
            add_drop_start=now - timedelta(days=5),
            add_drop_end=now + timedelta(days=15),
            emergency_drop_start=now + timedelta(days=20),
            emergency_drop_end=now + timedelta(days=25),
            is_active=True,
        )

        teacher = Teacher.objects.create(
            person=cls.professor_person,
            teacher_code="GRD-T-001",
            department=cls.department,
            hire_date=date(2015, 9, 1),
        )

        lesson = Lesson.objects.create(
            lesson_code="GRD-L-001",
            title="درس آزمایشی نمرات",
            theory_units=3,
            practical_units=0,
            department=cls.department,
        )

        classroom = Classroom.objects.create(
            building_name="ساختمان تست",
            room_number="GRD-01",
            capacity=40,
            classroom_type="کلاس",
        )

        cls.offering = CourseOffering.objects.create(
            lesson=lesson,
            term=cls.term,
            teacher=teacher,
            capacity=30,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom=classroom,
            is_active=True,
        )

        cls.enrollment = Enrollment.objects.create(
            student=cls.student,
            offering=cls.offering,
            status=enrollment_status,
        )

    @classmethod
    def make_person(cls, username, national_id):
        return Person.objects.create_user(
            username=username,
            password="TestPassword@123",
            first_name=username,
            last_name="آزمایش",
            email=f"{username}@example.com",
            national_id=national_id,
            birth_date=date(2001, 1, 1),
            birth_place="تهران",
        )

    def authenticate_account(self, person, account):
        self.client.force_login(person)
        session = self.client.session
        session["user_account_id"] = account.pk
        session.save()

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def put_json(self, url, payload):
        return self.client.put(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_student_can_view_own_grades(self):
        Grade.objects.create(
            enrollment=self.enrollment,
            score=Decimal("17.50"),
        )
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.client.get(
            reverse("grading:my-grades")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["score"],
            "17.50",
        )

    def test_professor_can_create_and_update_grade_without_duplicates(self):
        self.authenticate_account(
            self.professor_person,
            self.professor_account,
        )
        url = reverse(
            "grading:set-grade",
            args=[self.enrollment.pk],
        )

        first = self.put_json(url, {"score": "16.25"})
        self.assertEqual(first.status_code, 200)
        self.assertEqual(Grade.objects.filter(
            enrollment=self.enrollment
        ).count(), 1)

        second = self.put_json(url, {"score": "18.50"})
        self.assertEqual(second.status_code, 200)
        self.assertEqual(Grade.objects.filter(
            enrollment=self.enrollment
        ).count(), 1)

        grade = Grade.objects.get(enrollment=self.enrollment)
        self.assertEqual(grade.score, Decimal("18.50"))

    def test_professor_cannot_submit_invalid_grade(self):
        self.authenticate_account(
            self.professor_person,
            self.professor_account,
        )
        url = reverse(
            "grading:set-grade",
            args=[self.enrollment.pk],
        )

        for invalid_score in ("-1", "20.01", "abc", True):
            response = self.put_json(
                url,
                {"score": invalid_score},
            )
            self.assertEqual(response.status_code, 400)

        self.assertEqual(Grade.objects.count(), 0)

    def test_student_cannot_access_professor_grade_endpoint(self):
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.put_json(
            reverse(
                "grading:set-grade",
                args=[self.enrollment.pk],
            ),
            {"score": "18"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Grade.objects.count(), 0)

    def test_student_cannot_submit_appeal_before_grade_is_published(self):
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.post_json(
            reverse(
                "grading:create-appeal",
                args=[self.enrollment.pk],
            ),
            {"appeal_reason": "درخواست بررسی مجدد نمره"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "grade_not_available",
        )
        self.assertEqual(GradeAppeal.objects.count(), 0)

    def test_student_can_submit_appeal_after_grade_is_published(self):
        Grade.objects.create(
            enrollment=self.enrollment,
            score=Decimal("12.00"),
        )
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.post_json(
            reverse(
                "grading:create-appeal",
                args=[self.enrollment.pk],
            ),
            {"appeal_reason": "لطفاً نمره را دوباره بررسی کنید."},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(GradeAppeal.objects.count(), 1)

        appeal = GradeAppeal.objects.get()
        self.assertEqual(appeal.appeal_status.code, "submitted")

    def test_student_cannot_submit_empty_appeal_reason(self):
        Grade.objects.create(
            enrollment=self.enrollment,
            score=Decimal("12.00"),
        )
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.post_json(
            reverse(
                "grading:create-appeal",
                args=[self.enrollment.pk],
            ),
            {"appeal_reason": "   "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(GradeAppeal.objects.count(), 0)

    def test_student_can_submit_teacher_survey_once(self):
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )
        url = reverse(
            "grading:create-survey",
            args=[self.enrollment.pk],
        )
        payload = {
            "overall_rating": 5,
            "teaching_quality": 4,
            "behavior": 5,
            "comment": "تدریس بسیار خوب بود.",
        }

        first = self.post_json(url, payload)
        self.assertEqual(first.status_code, 201)
        self.assertEqual(TeacherSurvey.objects.count(), 1)

        second = self.post_json(url, payload)
        self.assertEqual(second.status_code, 409)
        self.assertEqual(TeacherSurvey.objects.count(), 1)

    def test_student_cannot_submit_invalid_teacher_survey_rating(self):
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.post_json(
            reverse(
                "grading:create-survey",
                args=[self.enrollment.pk],
            ),
            {"overall_rating": 6},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(TeacherSurvey.objects.count(), 0)

    def test_anonymous_user_cannot_view_grades(self):
        response = self.client.get(
            reverse("grading:my-grades")
        )

        self.assertEqual(response.status_code, 401)

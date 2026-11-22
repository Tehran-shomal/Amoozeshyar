import json
from datetime import date, time, timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from apps.core.models import (
    Attendance,
    Classroom,
    Constant,
    CourseOffering,
    Department,
    Enrollment,
    Faculty,
    Field,
    Lesson,
    Person,
    Role,
    Student,
    Teacher,
    Term,
    UserAccount,
)


class AttendanceAPITests(TestCase):

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
        cls.present_status = constant(
            "attendance_status", "present", "حاضر"
        )
        cls.absent_status = constant(
            "attendance_status", "absent", "غایب"
        )

        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده تست حضور",
            faculty_code="ATT",
        )
        cls.department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه تست حضور",
            department_code="ATT",
        )
        cls.field = Field.objects.create(
            department=cls.department,
            field_name="رشته تست حضور",
            field_code="ATT",
        )

        cls.student_person = cls.make_person(
            "attendance-student", "9812000001"
        )
        cls.professor_person = cls.make_person(
            "attendance-professor", "9812000002"
        )
        cls.other_professor_person = cls.make_person(
            "attendance-other-professor", "9812000003"
        )

        cls.student = Student.objects.create(
            person=cls.student_person,
            student_code="ATT-S-001",
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
            username="attendance-student-account",
            password="not-used",
        )
        cls.professor_account = UserAccount.objects.create(
            person=cls.professor_person,
            role=professor_role,
            username="attendance-professor-account",
            password="not-used",
        )
        cls.other_professor_account = UserAccount.objects.create(
            person=cls.other_professor_person,
            role=professor_role,
            username="attendance-other-professor-account",
            password="not-used",
        )

        now = timezone.now()
        term = Term.objects.create(
            term_code="ATT-1405",
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
            teacher_code="ATT-T-001",
            department=cls.department,
            hire_date=date(2015, 9, 1),
        )

        lesson = Lesson.objects.create(
            lesson_code="ATT-L-001",
            title="درس آزمایشی حضور و غیاب",
            theory_units=3,
            practical_units=0,
            department=cls.department,
        )

        classroom = Classroom.objects.create(
            building_name="ساختمان تست",
            room_number="ATT-01",
            capacity=40,
            classroom_type="کلاس",
        )

        cls.offering = CourseOffering.objects.create(
            lesson=lesson,
            term=term,
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

    def attendance_payload(self, **overrides):
        payload = {
            "session_number": 1,
            "session_date": date.today().isoformat(),
            "attendance_time": "08:15:00",
            "attendance_status_code": "present",
            "description": "ثبت حضور آزمایشی",
        }
        payload.update(overrides)
        return payload

    def test_professor_can_record_and_update_attendance(self):
        self.authenticate_account(
            self.professor_person,
            self.professor_account,
        )
        url = reverse(
            "attendance:record-attendance",
            args=[self.enrollment.pk],
        )

        first = self.post_json(
            url,
            self.attendance_payload(),
        )
        self.assertEqual(first.status_code, 201)
        self.assertTrue(first.json()["created"])
        self.assertEqual(Attendance.objects.count(), 1)

        second = self.post_json(
            url,
            self.attendance_payload(
                attendance_status_code="absent",
                description="اصلاح وضعیت جلسه",
            ),
        )
        self.assertEqual(second.status_code, 200)
        self.assertFalse(second.json()["created"])
        self.assertEqual(Attendance.objects.count(), 1)

        record = Attendance.objects.get()
        self.assertEqual(record.attendance_status.code, "absent")
        self.assertEqual(record.description, "اصلاح وضعیت جلسه")

    def test_professor_cannot_record_attendance_for_another_teachers_enrollment(self):
        self.authenticate_account(
            self.other_professor_person,
            self.other_professor_account,
        )

        response = self.post_json(
            reverse(
                "attendance:record-attendance",
                args=[self.enrollment.pk],
            ),
            self.attendance_payload(),
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_attendance_rejects_invalid_session_number(self):
        self.authenticate_account(
            self.professor_person,
            self.professor_account,
        )

        response = self.post_json(
            reverse(
                "attendance:record-attendance",
                args=[self.enrollment.pk],
            ),
            self.attendance_payload(session_number=0),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_attendance_rejects_invalid_status(self):
        self.authenticate_account(
            self.professor_person,
            self.professor_account,
        )

        response = self.post_json(
            reverse(
                "attendance:record-attendance",
                args=[self.enrollment.pk],
            ),
            self.attendance_payload(
                attendance_status_code="unknown-status"
            ),
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_student_can_view_own_attendance(self):
        Attendance.objects.create(
            enrollment=self.enrollment,
            session_number=1,
            session_date=date.today(),
            attendance_status=self.present_status,
            attendance_time=time(8, 15),
            description="حضور",
            recorded_by=self.professor_account,
        )

        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.client.get(
            reverse("attendance:my-attendance")
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["status"]["code"],
            "present",
        )

    def test_student_cannot_record_attendance(self):
        self.authenticate_account(
            self.student_person,
            self.student_account,
        )

        response = self.post_json(
            reverse(
                "attendance:record-attendance",
                args=[self.enrollment.pk],
            ),
            self.attendance_payload(),
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Attendance.objects.count(), 0)

    def test_anonymous_user_cannot_view_attendance(self):
        response = self.client.get(
            reverse("attendance:my-attendance")
        )

        self.assertEqual(response.status_code, 401)

import importlib
from datetime import date, time, timedelta

from django.test import TestCase
from django.utils import timezone

from apps.core.models import (
    Classroom,
    Constant,
    CourseOffering,
    Department,
    Faculty,
    Lesson,
    Person,
    Teacher,
    Term,
)


class SchedulingFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        now = timezone.now()
        semester = Constant.objects.create(
            category="semester",
            code="mehr",
            label="مهر",
        )
        cls.saturday = Constant.objects.create(
            category="day_of_week",
            code="saturday",
            label="شنبه",
        )
        cls.faculty = Faculty.objects.create(
            faculty_name="دانشکده زمان‌بندی",
            faculty_code="SCH",
        )
        cls.department = Department.objects.create(
            faculty=cls.faculty,
            department_name="گروه زمان‌بندی",
            department_code="SCH",
        )
        cls.active_term = Term.objects.create(
            term_code="S-14051",
            semester=semester,
            academic_year="1405-1406",
            start_date=date.today() - timedelta(days=30),
            end_date=date.today() + timedelta(days=150),
            registration_start=now - timedelta(days=1),
            registration_end=now + timedelta(days=1),
            add_drop_start=now + timedelta(days=2),
            add_drop_end=now + timedelta(days=3),
            emergency_drop_start=now + timedelta(days=4),
            emergency_drop_end=now + timedelta(days=5),
            is_active=True,
        )
        cls.inactive_term = Term.objects.create(
            term_code="S-14041",
            semester=semester,
            academic_year="1404-1405",
            start_date=date.today() - timedelta(days=400),
            end_date=date.today() - timedelta(days=200),
            registration_start=now - timedelta(days=500),
            registration_end=now - timedelta(days=490),
            add_drop_start=now - timedelta(days=480),
            add_drop_end=now - timedelta(days=470),
            emergency_drop_start=now - timedelta(days=460),
            emergency_drop_end=now - timedelta(days=450),
            is_active=False,
        )
        cls.active_offering = cls.create_offering(
            "ACTIVE",
            cls.active_term,
            time(8, 0),
            True,
        )
        cls.inactive_offering = cls.create_offering(
            "INACTIVE",
            cls.active_term,
            time(10, 0),
            False,
        )
        cls.old_offering = cls.create_offering(
            "OLD",
            cls.inactive_term,
            time(12, 0),
            True,
        )

    @classmethod
    def create_offering(cls, suffix, term, start_time, active):
        lesson = Lesson.objects.create(
            lesson_code=f"SCH-{suffix}",
            title=f"درس {suffix}",
            theory_units=3,
            practical_units=0,
            department=cls.department,
        )
        teacher_person = Person.objects.create_user(
            username=f"teacher-{suffix.lower()}",
            password="Person@Password1",
            first_name="استاد",
            last_name=suffix,
            email=f"teacher-{suffix.lower()}@example.com",
            national_id=f"003{len(suffix):07}",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        teacher = Teacher.objects.create(
            person=teacher_person,
            teacher_code=f"T-{suffix}",
            department=cls.department,
            hire_date=date(2010, 9, 1),
        )
        classroom = Classroom.objects.create(
            building_name="ساختمان زمان‌بندی",
            room_number=f"R-{suffix}",
            capacity=30,
            classroom_type="کلاس",
        )
        return CourseOffering.objects.create(
            lesson=lesson,
            term=term,
            teacher=teacher,
            capacity=20,
            day_of_week=cls.saturday,
            start_time=start_time,
            end_time=time(start_time.hour + 1, 0),
            classroom=classroom,
            is_active=active,
        )


class SchedulingServiceTests(SchedulingFixtures):
    def service(self):
        try:
            return importlib.import_module("apps.core.scheduling.services")
        except ModuleNotFoundError:
            self.fail("apps.core.scheduling.services is not implemented")

    def test_active_term_and_offering_list_use_only_active_records(self):
        active_term = getattr(self.service(), "get_active_term", None)
        list_offerings = getattr(self.service(), "list_offerings", None)
        self.assertTrue(callable(active_term), "get_active_term is not implemented")
        self.assertTrue(callable(list_offerings), "list_offerings is not implemented")

        self.assertEqual(active_term().pk, self.active_term.pk)
        self.assertEqual(list(list_offerings()), [self.active_offering])


class SchedulingAPITests(SchedulingFixtures):
    def test_active_term_endpoint_returns_safe_term_fields(self):
        response = self.client.get("/api/scheduling/active-term/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["term"],
            {
                "id": self.active_term.pk,
                "term_code": "S-14051",
                "academic_year": "1405-1406",
                "start_date": self.active_term.start_date.isoformat(),
                "end_date": self.active_term.end_date.isoformat(),
                "registration_open": True,
                "add_drop_open": False,
                "emergency_drop_open": False,
            },
        )

    def test_offerings_endpoint_returns_active_term_courses(self):
        response = self.client.get("/api/scheduling/offerings/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()["offerings"]
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["id"], self.active_offering.pk)
        self.assertEqual(payload[0]["lesson_code"], "SCH-ACTIVE")
        self.assertEqual(payload[0]["remaining_capacity"], 20)

    def test_offerings_endpoint_can_read_a_selected_historical_term(self):
        response = self.client.get(
            "/api/scheduling/offerings/?term=S-14041"
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()["offerings"]
        self.assertEqual([item["id"] for item in payload], [self.old_offering.pk])

    def test_offerings_endpoint_rejects_unknown_term_codes(self):
        response = self.client.get("/api/scheduling/offerings/?term=missing")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "term_not_found")


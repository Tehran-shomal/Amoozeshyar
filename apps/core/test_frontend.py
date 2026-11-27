"""آزمون جریان واقعی صفحه‌ها روی دیتابیس تست مستقل از دیتابیس محلی."""
from datetime import date, timedelta
from contextlib import redirect_stdout
from io import StringIO
import json
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.test import SimpleTestCase
from django.test import tag
from django.utils import timezone
from apps.core import models as m
import re


class FrontendTeamStructureTests(SimpleTestCase):
    def test_date_payload_formatter_accepts_plain_date_values(self):
        from apps.core.frontend.react_payloads import _date_display

        self.assertEqual(_date_display(date(2026, 11, 27)), "2026/11/27")

    def test_team_manifests_cover_each_portal_page_once(self):
        from apps.core.frontend.registry import GROUPS, PAGES

        self.assertEqual(len(GROUPS), 7)
        declared = []
        for owner, (_, module) in GROUPS.items():
            self.assertTrue(hasattr(module, "PAGES"), f"{owner} must declare its pages")
            declared.extend(module.PAGES)

        self.assertEqual(len(declared), len(set(declared)), "a page has more than one owner")
        self.assertEqual(set(declared), set(PAGES))

    def test_frontend_lead_and_special_pages_are_explicit(self):
        from apps.core.frontend.registry import GROUPS
        from apps.core.frontend.mobina import SPECIAL_PAGES
        from apps.core.frontend.niousha import COMPONENTS

        self.assertEqual(GROUPS["niousha"][0], "نیوشا (لید فرانت)")
        self.assertEqual(set(SPECIAL_PAGES), {"login", "dashboard"})
        self.assertIn("term_picker", COMPONENTS)
        self.assertEqual(set(GROUPS), {
            "mobina", "shaghayegh", "parsa", "omid", "niousha", "shahsvand", "miri"
        })
        self.assertEqual(set(GROUPS["miri"][1].PAGES), {
            "evaluation", "evaluation-form", "messages", "announcements", "notifications",
            "guide", "support",
        })


class LiveFrontendTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        faculty = m.Faculty.objects.create(faculty_name="دانشکده", faculty_code="F")
        dep = m.Department.objects.create(faculty=faculty, department_name="گروه", department_code="D")
        field = m.Field.objects.create(department=dep, field_name="رشته آزمایشی", field_code="C")
        cls.users, cls.students = [], []
        for i in range(2):
            person = m.Person.objects.create_user(username=f"student{i}", password="test-pass",
                first_name=f"دانشجو{i}", last_name="آزمون", email=f"{i}@example.com",
                national_id=f"{i:010}", birth_date=date(2000, 1, i+1), birth_place="تهران")
            cls.users.append(person)
            cls.students.append(m.Student.objects.create(person=person, field=field,
                student_code=f"S{i}", application_date=date(2024, 1, 1)))
        now = timezone.now()
        cls.term = m.Term.objects.create(term_code="T1", academic_year="1405-1406",
            start_date=date(2026, 1, 1), end_date=date(2027, 1, 1),
            registration_start=now-timedelta(days=1), registration_end=now+timedelta(days=1),
            add_drop_start=now-timedelta(days=1), add_drop_end=now+timedelta(days=1),
            emergency_drop_start=now-timedelta(days=1), emergency_drop_end=now+timedelta(days=1), is_active=True)
        m.Constant.objects.get_or_create(category="review_status", code="pending", defaults={"label":"در انتظار"})
        cls.kind = m.Constant.objects.create(category="service_request_type", code="certificate", label="گواهی")
        m.Constant.objects.create(
            category="service_request_type", code="employment_certificate", label="گواهی اشتغال"
        )
        m.Constant.objects.create(
            category="internship_request_type", code="internship", label="درخواست کارآموزی"
        )

    def test_anonymous_pages_require_login(self):
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/portal/payments/").status_code, 302)
        self.assertEqual(self.client.get("/login/").status_code, 200)

    def test_enrollment_stage_one_uses_owned_profile_and_live_term_without_inventing_minimum_units(self):
        self.client.force_login(self.users[0])
        self.students[0].tuition_debt = 12_000_000
        self.students[0].save(update_fields=["tuition_debt"])

        response = self.client.get(
            "/api/portal/pages/enrollment/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="enrollment-steps"', html)
        self.assertIn(self.users[0].full_name, html)
        self.assertIn("S0", html)
        self.assertIn(self.term.academic_year, html)
        self.assertRegex(html, r"12[،,]?000[،,]?000")
        self.assertIn('href="/portal/selected-courses/', html)
        self.assertNotIn("حداقل واحد", html)

    def test_all_pages_render_without_demo_person(self):
        from apps.core.frontend.registry import PAGES, GROUPS
        self.assertEqual(len(GROUPS), 7)
        self.client.force_login(self.users[0])
        for slug in PAGES:
            response = self.client.get(f"/portal/{slug}/")
            self.assertEqual(response.status_code, 200, slug)
            self.assertContains(response, 'data-portal-loading="true"', msg_prefix=slug)
            self.assertContains(
                response,
                f'data-page-api-url="/api/portal/pages/{slug}/"',
                msg_prefix=slug,
            )
            self.assertNotContains(response, self.users[0].full_name, msg_prefix=slug)
            self.assertNotContains(response, "ali.mohammadi@example.edu")
            api_response = self.client.get(f"/api/portal/pages/{slug}/")
            self.assertEqual(api_response.status_code, 200, slug)
            self.assertNotIn("ali.mohammadi@example.edu", api_response.json()["html"])
        home_shell = self.client.get("/")
        self.assertContains(
            home_shell,
            'data-page-api-url="/api/portal/pages/home/"',
        )
        self.assertNotContains(home_shell, "دانشجو0")
        self.assertIn("دانشجو0", self.client.get("/api/portal/pages/home/").json()["html"])

    def test_student_and_exam_cards_use_page_specific_real_data_templates(self):
        self.client.force_login(self.users[0])

        student_card = self.client.get("/api/portal/pages/student-card/").json()["html"]
        self.assertIn('class="digital-card"', student_card)
        self.assertIn(self.users[0].full_name, student_card)
        self.assertIn("S0", student_card)
        self.assertNotIn("23456789", student_card)

        exam_card = self.client.get("/api/portal/pages/exam-card/").json()["html"]
        self.assertIn("exam-card-student", exam_card)
        self.assertIn("exam-card-table", exam_card)
        self.assertIn("صدور کارت رسمی در دسترس نیست", exam_card)
        self.assertNotIn("data-demo-action", exam_card)
        self.assertNotIn("سالن ۱", exam_card)

    def test_exam_card_debt_blocker_shows_the_persisted_amount_in_rials(self):
        self.client.force_login(self.users[0])
        student = self.students[0]
        student.tuition_debt = 987654
        student.save(update_fields=["tuition_debt"])

        response = self.client.get("/api/portal/pages/exam-card/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("987,654 ریال", response.json()["html"])

    def test_schedule_page_renders_owned_enrollments_in_a_weekly_grid(self):
        from datetime import time

        self.client.force_login(self.users[0])
        department = m.Department.objects.get(department_code="D")
        day = m.Constant.objects.create(
            category="day_of_week", code="saturday", label="شنبه"
        )
        status = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="ثبت‌شده"
        )
        teacher = m.Teacher.objects.create(
            person=self.users[1],
            teacher_code="T-SCHEDULE",
            department=department,
            hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان برنامه",
            room_number="۱۰۱",
            capacity=30,
            classroom_type="کلاس",
        )
        lesson = m.Lesson.objects.create(
            lesson_code="L-SCHEDULE",
            title="پایگاه داده",
            theory_units=3,
            practical_units=0,
            department=department,
        )
        offering = m.CourseOffering.objects.create(
            lesson=lesson,
            term=self.term,
            teacher=teacher,
            capacity=30,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom=classroom,
            is_active=True,
        )
        m.Enrollment.objects.create(
            student=self.students[0], offering=offering, status=status
        )

        response = self.client.get("/api/portal/pages/schedule/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("weekly-schedule-grid", html)
        self.assertIn('data-schedule-units="3"', html)
        self.assertIn('data-schedule-sessions="1"', html)
        self.assertIn('data-schedule-conflicts="false"', html)
        self.assertIn("شنبه", html)
        self.assertIn("پایگاه داده", html)
        self.assertIn("دانشجو1 آزمون", html)
        self.assertIn("ساختمان برنامه - ۱۰۱", html)
        self.assertNotIn('class="data-table"', html)

    def test_curriculum_page_shows_chart_progress_and_real_course_state(self):
        from datetime import time

        self.client.force_login(self.users[0])
        department = m.Department.objects.get(department_code="D")
        required = m.Constant.objects.create(
            category="requirement_type", code="major", label="اصلی"
        )
        enrolled = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="ثبت‌شده"
        )
        prerequisite_type = m.Constant.objects.create(
            category="prerequisite_type", code="prerequisite", label="پیش‌نیاز"
        )
        completed = m.Lesson.objects.create(
            lesson_code="L-CUR-1", title="درس گذرانده", theory_units=3,
            department=department,
        )
        current = m.Lesson.objects.create(
            lesson_code="L-CUR-2", title="درس جاری", theory_units=4,
            department=department,
        )
        remaining = m.Lesson.objects.create(
            lesson_code="L-CUR-3", title="درس باقی‌مانده", theory_units=2,
            department=department,
        )
        for lesson, units, suggested_term in (
            (completed, 3, 1), (current, 4, 2), (remaining, 2, 3)
        ):
            m.Curriculum.objects.create(
                field=self.students[0].field, lesson=lesson,
                requirement_type=required, recommended_term=suggested_term,
                calculated_units=units,
            )
        m.Prerequisite.objects.create(
            lesson=current, prerequisite_lesson=completed,
            prerequisite_type=prerequisite_type,
        )
        teacher = m.Teacher.objects.create(
            person=self.users[1], teacher_code="T-CURRICULUM",
            department=department, hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان چارت", room_number="۱۰۲", capacity=30,
            classroom_type="کلاس",
        )
        for lesson, start in ((completed, time(8, 0)), (current, time(10, 0))):
            offering = m.CourseOffering.objects.create(
                lesson=lesson, term=self.term, teacher=teacher, capacity=30,
                start_time=start, end_time=time(start.hour + 2, 0),
                classroom=classroom,
            )
            enrollment = m.Enrollment.objects.create(
                student=self.students[0], offering=offering, status=enrolled,
            )
            if lesson == completed:
                m.Grade.objects.create(enrollment=enrollment, score=18)
        other_student_offering = m.CourseOffering.objects.create(
            lesson=remaining, term=self.term, teacher=teacher, capacity=30,
            start_time=time(12, 0), end_time=time(14, 0), classroom=classroom,
        )
        other_student_enrollment = m.Enrollment.objects.create(
            student=self.students[1], offering=other_student_offering, status=enrolled,
        )
        m.Grade.objects.create(enrollment=other_student_enrollment, score=20)

        response = self.client.get("/api/portal/pages/curriculum/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('data-curriculum-total="9"', html)
        self.assertIn('data-curriculum-passed="3"', html)
        self.assertIn('data-curriculum-current="4"', html)
        self.assertIn('data-curriculum-remaining="2"', html)
        self.assertIn("درس گذرانده", html)
        self.assertIn("درس جاری", html)
        self.assertIn("درس باقی‌مانده", html)
        self.assertIn("پیش‌نیاز: درس گذرانده", html)
        self.assertIn("گذرانده", html)
        self.assertIn("جاری", html)
        self.assertIn("اصلی", html)
        self.assertNotIn('class="data-table"', html)

    def test_internship_page_uses_owned_form_and_scoped_request_history(self):
        self.client.force_login(self.users[0])
        request_type = m.Constant.objects.get(
            category="internship_request_type", code="internship"
        )
        pending = m.Constant.objects.get(
            category="review_status", code="pending"
        )
        m.Internship.objects.create(
            student=self.students[0], request_type=request_type,
            company_name="سازمان پروندهٔ من", intern_start_date=date(2026, 12, 1),
            duration_hours=120, status=pending,
        )
        m.Internship.objects.create(
            student=self.students[1], request_type=request_type,
            company_name="سازمان پروندهٔ دیگر", intern_start_date=date(2026, 12, 1),
            duration_hours=240, status=pending,
        )

        response = self.client.get("/api/portal/pages/internship/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("internship-application-form", html)
        self.assertIn('name="request_type"', html)
        self.assertIn('name="company_name"', html)
        self.assertIn('name="intern_start_date"', html)
        self.assertIn('name="duration_hours"', html)
        self.assertIn("سازمان پروندهٔ من", html)
        self.assertIn("در انتظار", html)
        self.assertNotIn("سازمان پروندهٔ دیگر", html)
        self.assertNotIn('name="supervisor"', html)

    def test_internship_submission_shows_only_the_owned_persisted_result(self):
        self.client.force_login(self.users[0])
        request_type = m.Constant.objects.get(
            category="internship_request_type", code="internship"
        )

        submitted = self.client.post(
            "/api/portal/pages/internship/?student_code=S0&term=T1",
            data=json.dumps({
                "request_type": request_type.pk,
                "company_name": "سازمان ثبت‌شده",
                "intern_start_date": "2026-12-10",
                "duration_hours": 40,
            }),
            content_type="application/json",
        )

        self.assertEqual(submitted.status_code, 200)
        saved = m.Internship.objects.get(
            student=self.students[0], company_name="سازمان ثبت‌شده"
        )
        self.assertIn(f"request_id={saved.pk}", submitted.json()["redirect"])

        result = self.client.get(
            f"/api/portal/pages/internship/?student_code=S0&term=T1&request_id={saved.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="internship-submission-result"', html)
        self.assertIn("سازمان ثبت‌شده", html)
        self.assertIn("ارسال به سامانهٔ دانشگاه انجام نشده است", html)

        other_request = m.Internship.objects.create(
            student=self.students[1], request_type=request_type,
            company_name="سازمان پروندهٔ دیگر", intern_start_date=date(2026, 12, 10),
            duration_hours=40,
        )
        foreign_result = self.client.get(
            f"/api/portal/pages/internship/?student_code=S0&term=T1&request_id={other_request.pk}"
        )
        self.assertEqual(foreign_result.status_code, 200)
        self.assertNotIn('class="internship-submission-result"', foreign_result.json()["html"])

    def test_guest_request_page_shows_real_destination_and_owned_status(self):
        self.client.force_login(self.users[0])
        pending = m.Constant.objects.get(
            category="review_status", code="pending"
        )
        m.TransferRequest.objects.create(
            student=self.students[0], destination_university="دانشگاه مقصد پروندهٔ من",
            review_status=pending,
        )
        m.TransferRequest.objects.create(
            student=self.students[1], destination_university="دانشگاه پروندهٔ دیگر",
            review_status=pending,
        )

        response = self.client.get("/api/portal/pages/guest-request/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("guest-request-application-form", html)
        self.assertIn('name="destination_university"', html)
        self.assertIn("دانشگاه مقصد پروندهٔ من", html)
        self.assertIn("در انتظار", html)
        self.assertNotIn("دانشگاه پروندهٔ دیگر", html)
        self.assertNotIn('name="origin_university"', html)
        self.assertNotIn('type="file"', html)

    def test_guest_request_submission_shows_only_the_owned_persisted_result(self):
        self.client.force_login(self.users[0])

        submitted = self.client.post(
            "/api/portal/pages/guest-request/?student_code=S0&term=T1",
            data=json.dumps({"destination_university": "دانشگاه مقصد ثبت‌شده"}),
            content_type="application/json",
        )

        self.assertEqual(submitted.status_code, 200)
        saved = m.TransferRequest.objects.get(
            student=self.students[0], destination_university="دانشگاه مقصد ثبت‌شده"
        )
        self.assertIn(f"request_id={saved.pk}", submitted.json()["redirect"])

        result = self.client.get(
            f"/api/portal/pages/guest-request/?student_code=S0&term=T1&request_id={saved.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="guest-request-submission-result"', html)
        self.assertIn("دانشگاه مقصد ثبت‌شده", html)
        self.assertIn("وضعیت بررسی", html)
        self.assertIn("تأیید نهایی پس از بررسی انجام می‌شود", html)

        other_request = m.TransferRequest.objects.create(
            student=self.students[1], destination_university="دانشگاه مقصد پروندهٔ دیگر"
        )
        foreign_result = self.client.get(
            f"/api/portal/pages/guest-request/?student_code=S0&term=T1&request_id={other_request.pk}"
        )
        self.assertEqual(foreign_result.status_code, 200)
        self.assertNotIn('class="guest-request-submission-result"', foreign_result.json()["html"])

    def test_graduation_page_reports_only_recorded_audit_and_profile_facts(self):
        self.client.force_login(self.users[0])
        department = m.Department.objects.get(department_code="D")
        lesson = m.Lesson.objects.create(
            lesson_code="L-GRAD", title="درس چارت", theory_units=3,
            department=department,
        )
        curriculum = m.Curriculum.objects.create(
            field=self.students[0].field, lesson=lesson, recommended_term=1,
            calculated_units=3,
        )
        eligible = m.Constant.objects.create(
            category="graduation_status", code="eligible", label="واجد شرایط"
        )
        self.students[0].passed_units = 3
        self.students[0].total_gpa = "15.75"
        self.students[0].tuition_debt = 250000
        self.students[0].save(update_fields=["passed_units", "total_gpa", "tuition_debt"])
        m.GraduationAudit.objects.create(
            student=self.students[0], curriculum=curriculum,
            graduation_status=eligible,
        )
        m.GraduationAudit.objects.create(
            student=self.students[1], curriculum=curriculum,
            graduation_status=eligible,
        )

        response = self.client.get("/api/portal/pages/graduation/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("graduation-checklist-panel", html)
        self.assertIn('data-graduation-audits="1"', html)
        self.assertIn("واجد شرایط", html)
        self.assertIn("واحد باقیمانده", html)
        self.assertIn("15.75", html)
        self.assertIn("250,000 ریال", html)
        self.assertIn("در این نسخه قابل بررسی نیست", html)
        self.assertNotIn("درخواست فارغ‌التحصیلی ثبت شد", html)
        self.assertNotIn('class="live-form', html)

        post_response = self.client.post(
            "/api/portal/pages/graduation/",
            data=json.dumps({}), content_type="application/json",
        )
        self.assertEqual(post_response.status_code, 405)

    def test_message_recipients_and_submission_results_are_account_scoped(self):
        from datetime import time

        self.client.force_login(self.users[0])
        department = m.Department.objects.get(department_code="D")
        active_teacher = m.Teacher.objects.create(
            person=self.users[1], teacher_code="T-MSG-ACTIVE",
            department=department, hire_date=date(2010, 1, 1),
        )
        other_teacher_person = m.Person.objects.create_user(
            username="term-two-teacher", password="test-pass",
            first_name="استاد", last_name="نیمسال دیگر",
            email="term-two-teacher@example.com", national_id="0000000004",
            birth_date=date(1980, 1, 1), birth_place="تهران",
        )
        other_teacher = m.Teacher.objects.create(
            person=other_teacher_person, teacher_code="T-MSG-OTHER",
            department=department, hire_date=date(2010, 1, 1),
        )
        teacher_role = m.Role.objects.create(role_name="message-teacher")
        student_role = m.Role.objects.create(role_name="message-student")
        m.UserAccount.objects.create(
            person=self.users[0], role=student_role, username="message-student",
            password="unused",
        )
        m.UserAccount.objects.create(
            person=self.users[1], role=teacher_role, username="message-active-teacher",
            password="unused",
        )
        m.UserAccount.objects.create(
            person=other_teacher_person, role=teacher_role,
            username="message-other-teacher", password="unused",
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان پیام", room_number="۱۰۳", capacity=30,
            classroom_type="کلاس",
        )
        active_lesson = m.Lesson.objects.create(
            lesson_code="L-MSG-1", title="درس نیمسال جاری", theory_units=3,
            department=department,
        )
        other_lesson = m.Lesson.objects.create(
            lesson_code="L-MSG-2", title="درس نیمسال دیگر", theory_units=3,
            department=department,
        )
        registered = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="ثبت‌شده"
        )
        dropped = m.Constant.objects.create(
            category="enrollment_status", code="dropped", label="حذف‌شده"
        )
        active_offering = m.CourseOffering.objects.create(
            lesson=active_lesson, term=self.term, teacher=active_teacher,
            capacity=30, start_time=time(8, 0), end_time=time(10, 0),
            classroom=classroom,
        )
        m.Enrollment.objects.create(
            student=self.students[0], offering=active_offering, status=registered,
        )
        dropped_offering = m.CourseOffering.objects.create(
            lesson=other_lesson, term=self.term, teacher=other_teacher,
            capacity=30, start_time=time(10, 0), end_time=time(12, 0),
            classroom=classroom,
        )
        m.Enrollment.objects.create(
            student=self.students[0], offering=dropped_offering, status=dropped,
        )
        other_term = m.Term.objects.create(
            term_code="T2", academic_year="1406-1407",
            start_date=self.term.start_date, end_date=self.term.end_date,
            registration_start=self.term.registration_start,
            registration_end=self.term.registration_end,
            add_drop_start=self.term.add_drop_start,
            add_drop_end=self.term.add_drop_end,
            emergency_drop_start=self.term.emergency_drop_start,
            emergency_drop_end=self.term.emergency_drop_end,
            is_active=False,
        )
        other_term_offering = m.CourseOffering.objects.create(
            lesson=other_lesson, term=other_term, teacher=other_teacher,
            capacity=30, start_time=time(8, 0), end_time=time(10, 0),
            classroom=classroom,
        )
        m.Enrollment.objects.create(
            student=self.students[0], offering=other_term_offering, status=registered,
        )

        response = self.client.get("/api/portal/pages/messages/?term=T1")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        recipient_options = html.split('name="receiver"', 1)[1].split("</select>", 1)[0]
        self.assertIn(self.users[1].full_name, recipient_options)
        self.assertNotIn("استاد نیمسال دیگر", recipient_options)
        self.assertIn("درس نیمسال جاری", html)
        self.assertNotIn("درس نیمسال دیگر", html)

        student_account = m.UserAccount.objects.get(person=self.users[0])
        teacher_account = m.UserAccount.objects.get(person=self.users[1])
        submitted = self.client.post(
            "/api/portal/pages/messages/?student_code=S0&term=T1",
            data=json.dumps({
                "receiver": teacher_account.pk,
                "subject": "پرسش دربارهٔ درس",
                "message_body": "لطفاً زمان پاسخ‌گویی را اعلام کنید.",
            }),
            content_type="application/json",
        )
        self.assertEqual(submitted.status_code, 200)
        sent_message = m.Communication.objects.get(subject="پرسش دربارهٔ درس")
        self.assertEqual(sent_message.sender, student_account)
        self.assertEqual(sent_message.receiver, teacher_account)
        self.assertIn(f"request_id={sent_message.pk}", submitted.json()["redirect"])

        sent_result = self.client.get(
            f"/api/portal/pages/messages/?student_code=S0&term=T1&request_id={sent_message.pk}"
        )
        self.assertEqual(sent_result.status_code, 200)
        sent_html = sent_result.json()["html"]
        self.assertIn('class="message-submission-result"', sent_html)
        self.assertIn("پرسش دربارهٔ درس", sent_html)
        self.assertIn("تحویل بیرونی از این ثبت قابل تأیید نیست", sent_html)

        incoming_message = m.Communication.objects.create(
            sender=teacher_account, receiver=student_account,
            subject="پیام ورودی", message_body="این پیام توسط دانشجو ارسال نشده است.",
        )
        incoming_result = self.client.get(
            f"/api/portal/pages/messages/?student_code=S0&term=T1&request_id={incoming_message.pk}"
        )
        self.assertEqual(incoming_result.status_code, 200)
        self.assertNotIn('class="message-submission-result"', incoming_result.json()["html"])

    def test_registration_debt_error_has_a_real_data_backed_blocking_dialog(self):
        self.client.force_login(self.users[0])
        student = self.students[0]
        student.tuition_debt = 1200000
        student.save(update_fields=["tuition_debt"])

        response = self.client.get("/api/portal/pages/selected-courses/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('data-tuition-debt-modal', html)
        self.assertIn("عملیات ثبت‌نام مجاز نیست", html)
        self.assertIn("1200000", html)
        self.assertIn("حداقل واحد در قوانین جاری سامانه تعریف نشده است", html)
        self.assertIn('href="/portal/secure-payment/', html)
        self.assertIn('data-close-tuition-debt', html)

    def test_registration_debt_dialog_uses_the_same_probation_credit_limit_as_api(self):
        self.client.force_login(self.users[0])
        probation = m.Constant.objects.create(
            category="student_status", code="probation", label="مشروط",
        )
        student = self.students[0]
        student.status = probation
        student.previous_term_gpa = 18
        student.tuition_debt = 1
        student.save(update_fields=["status", "previous_term_gpa", "tuition_debt"])

        response = self.client.get("/api/portal/pages/selected-courses/")

        html = response.json()["html"]
        self.assertIn("14 واحد", html)
        self.assertNotIn("24 واحد", html)

    def test_add_drop_page_exposes_real_add_and_drop_actions_together(self):
        self.client.force_login(self.users[0])
        enrollment, _teacher = self._make_evaluation_enrollment(self.students[0], "8")

        response = self.client.get(
            "/api/portal/pages/add-drop/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn(enrollment.offering.lesson.title, html)
        self.assertIn("وضعیت</th>", html)
        self.assertIn(enrollment.status.label, html)
        self.assertIn('data-enrollment-action="drop"', html)
        self.assertIn('data-open-course-offerings', html)
        self.assertIn('id="course-offerings-panel"', html)
        self.assertIn('data-offerings-api-table', html)
        self.assertIn("تعرفهٔ شهریه برای این نیمسال", html)
        self.assertIn("حداقل واحد در API تعریف نشده است", html)
        self.assertIn("API فعلی مبلغ بازپرداخت را محاسبه یا ثبت نمی‌کند", html)

    def test_emergency_drop_page_marks_actions_for_its_specific_endpoint(self):
        self.client.force_login(self.users[0])
        enrollment, _teacher = self._make_evaluation_enrollment(self.students[0], "9")

        response = self.client.get(
            "/api/portal/pages/emergency-drop/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn(enrollment.offering.lesson.title, html)
        self.assertIn('data-enrollment-action="emergency-drop"', html)
        self.assertNotIn('data-enrollment-action="drop"', html)
        self.assertIn("درخواست استرداد وجه ایجاد نمی‌کند", html)
        self.assertIn("حذف اضطراری بازپرداخت ثبت نمی‌کند", html)

    def test_emergency_drop_result_shows_only_the_owned_dropped_enrollment(self):
        self.client.force_login(self.users[0])
        own_enrollment, _ = self._make_evaluation_enrollment(self.students[0], "75")
        foreign_enrollment, _ = self._make_evaluation_enrollment(self.students[1], "76")
        dropped = m.Constant.objects.create(
            category="enrollment_status", code="dropped", label="حذف‌شده"
        )
        own_enrollment.status = dropped
        own_enrollment.drop_date = date(2026, 8, 21)
        own_enrollment.save(update_fields=["status", "drop_date"])

        result = self.client.get(
            f"/api/portal/pages/emergency-drop/?student_code=S0&term=T1"
            f"&dropped_enrollment_id={own_enrollment.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="course-drop-result"', html)
        self.assertIn(own_enrollment.offering.lesson.title, html)
        self.assertIn(own_enrollment.offering.lesson.lesson_code, html)
        self.assertIn("حذف‌شده", html)
        self.assertIn("برای این حذف بازپرداخت مالی ثبت نشده است", html)
        self.assertNotIn(foreign_enrollment.offering.lesson.lesson_code, html)

        foreign_result = self.client.get(
            f"/api/portal/pages/emergency-drop/?student_code=S0&term=T1"
            f"&dropped_enrollment_id={foreign_enrollment.pk}"
        )
        self.assertNotIn('class="course-drop-result"', foreign_result.json()["html"])

    def test_add_drop_registration_result_is_scoped_to_an_owned_active_enrollment(self):
        self.client.force_login(self.users[0])
        own_enrollment, _teacher = self._make_evaluation_enrollment(self.students[0], "11")
        other_enrollment, _other_teacher = self._make_evaluation_enrollment(self.students[1], "12")

        own_result = self.client.get(
            f"/api/portal/pages/add-drop/?student_code=S0&term=T1&registration_id={own_enrollment.pk}"
        )
        self.assertEqual(own_result.status_code, 200)
        own_html = own_result.json()["html"]
        self.assertIn('class="course-registration-result"', own_html)
        self.assertIn(own_enrollment.offering.lesson.title, own_html)
        self.assertIn("در برنامهٔ این نیمسال ثبت فعال دارد", own_html)

        other_result = self.client.get(
            f"/api/portal/pages/add-drop/?student_code=S0&term=T1&registration_id={other_enrollment.pk}"
        )
        self.assertEqual(other_result.status_code, 200)
        self.assertNotIn('class="course-registration-result"', other_result.json()["html"])

    def test_registration_status_summarizes_persisted_stages_without_claiming_final_approval(self):
        self.client.force_login(self.users[0])
        enrollment, _teacher = self._make_evaluation_enrollment(self.students[0], "10")
        self.students[0].tuition_debt = 12_000_000
        self.students[0].save(update_fields=["tuition_debt"])

        response = self.client.get(
            "/api/portal/pages/registration-status/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="registration-status-page"', html)
        self.assertIn(enrollment.offering.lesson.title, html)
        self.assertIn("1 درس ثبت فعال", html)
        self.assertIn("بدهی ثبت‌شده در پرونده", html)
        self.assertIn("تأیید نهایی در داده‌های فعلی ثبت نشده است", html)
        self.assertNotIn("تأیید نهایی انجام شد", html)
        self.assertIn('href="/portal/secure-payment/', html)

    def test_selected_courses_matches_pdf_columns_and_hides_offerings_until_requested(self):
        from datetime import time

        self.client.force_login(self.users[0])
        day = m.Constant.objects.create(
            category="day_of_week", code="saturday", label="شنبه"
        )
        teacher_person = m.Person.objects.create_user(
            username="course-teacher",
            password="test-pass",
            first_name="استاد",
            last_name="آزمون",
            email="course-teacher@example.com",
            national_id="0000000003",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        teacher = m.Teacher.objects.create(
            person=teacher_person,
            teacher_code="T-TEST",
            department=self.field.department,
            hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان آزمون",
            room_number="۱۰۱",
            capacity=30,
            classroom_type="کلاس",
        )
        lesson = m.Lesson.objects.create(
            lesson_code="L-EXAM",
            title="درس نمونهٔ انتخاب‌شده",
            theory_units=3,
            department=self.field.department,
        )
        offering = m.CourseOffering.objects.create(
            lesson=lesson,
            term=self.term,
            teacher=teacher,
            capacity=30,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom=classroom,
            exam_date=date(2026, 1, 20),
            exam_time=time(8, 0),
            is_active=True,
        )
        status = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="ثبت‌شده"
        )
        m.Enrollment.objects.create(
            student=self.students[0], offering=offering, status=status
        )

        html = self.client.get(
            "/api/portal/pages/selected-courses/?term=T1"
        ).json()["html"]

        headers = ["نام درس", "کد درس", "واحد", "استاد", "زمان برگزاری", "زمان امتحان", "وضعیت"]
        table_header = html.split("<thead>", 1)[1].split("</thead>", 1)[0]
        positions = [table_header.index(header) for header in headers]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("2026-01-20 • 08:00", html)
        self.assertIn("data-open-course-offerings", html)
        self.assertIn('data-course-modal-opener', html)
        self.assertIn('data-course-modal', html)
        self.assertIn('data-course-modal-close', html)
        self.assertIn('data-course-modal-groups', html)
        self.assertIn('data-course-modal-exam', html)
        self.assertIn("شمارهٔ گروه در داده‌های سامانه ثبت نشده است", html)
        self.assertIn("تعرفهٔ هر درس در داده‌های سامانه ثبت نشده است", html)
        self.assertRegex(html, r'id="course-offerings-modal"[^>]*hidden')
        self.assertIn("شهریه ثابت", html)
        self.assertIn("شهریه متغیر", html)
        self.assertIn("تعرفهٔ شهریه برای این نیمسال در داده‌های سامانه ثبت نشده است", html)

    def test_calendar_page_renders_month_grid_and_real_term_events(self):
        self.client.force_login(self.users[0])

        html = self.client.get(
            "/api/portal/pages/calendar/?term=T1"
        ).json()["html"]

        self.assertIn('class="calendar-month-grid"', html)
        self.assertIn('data-date="2026-01-01"', html)
        self.assertIn("شروع نیمسال", html)
        self.assertIn("2026-01-01", html)
        self.assertIn("دی ۱۴۰۴", html)
        self.assertIn("۱۴۰۴/۱۰/۱۱", html)
        self.assertIn("بازه انتخاب واحد", html)

    def test_announcements_use_owned_announcement_communications_and_mark_read(self):
        self.client.force_login(self.users[0])
        teacher_person = m.Person.objects.create_user(
            username="announcement-teacher",
            password="test-pass",
            first_name="استاد",
            last_name="اطلاعیه",
            email="announcement-teacher@example.com",
            national_id="0000000010",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        teacher_role = m.Role.objects.create(role_name="announcement-teacher-role")
        student_role = m.Role.objects.create(role_name="announcement-student-role")
        teacher_account = m.UserAccount.objects.create(
            person=teacher_person, role=teacher_role,
            username="announcement-teacher-account", password="unused",
        )
        recipient = m.UserAccount.objects.create(
            person=self.users[0], role=student_role,
            username="announcement-recipient", password="unused",
        )
        other_recipient = m.UserAccount.objects.create(
            person=self.users[1], role=student_role,
            username="announcement-other-recipient", password="unused",
        )
        announcement_type = m.Constant.objects.create(
            category="communication_type", code="announcement", label="اطلاعیه"
        )
        official_type = m.Constant.objects.create(
            category="communication_type", code="official", label="رسمی"
        )
        unread = m.Constant.objects.create(
            category="communication_status", code="unread", label="خوانده‌نشده"
        )
        read = m.Constant.objects.create(
            category="communication_status", code="read", label="خوانده‌شده"
        )
        announcement = m.Communication.objects.create(
            sender=teacher_account, receiver=recipient,
            subject="اطلاعیهٔ ثبت‌شده", message_body="متن اطلاعیهٔ واقعی",
            communication_type=announcement_type, status=unread,
        )
        m.Communication.objects.create(
            sender=teacher_account, receiver=other_recipient,
            subject="اطلاعیهٔ حساب دیگر", message_body="نباید نمایش داده شود",
            communication_type=announcement_type, status=unread,
        )
        m.Communication.objects.create(
            sender=teacher_account, receiver=recipient,
            subject="مکاتبهٔ رسمی", message_body="این اطلاعیه نیست",
            communication_type=official_type, status=unread,
        )

        response = self.client.get("/api/portal/pages/announcements/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="announcement-card"', html)
        self.assertIn("اطلاعیهٔ ثبت‌شده", html)
        self.assertIn("استاد اطلاعیه", html)
        self.assertNotIn("اطلاعیهٔ حساب دیگر", html)
        self.assertNotIn("مکاتبهٔ رسمی", html)

        response = self.client.post(
            "/api/portal/pages/announcements/",
            data=json.dumps({"communication_id": announcement.communication_id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        announcement.refresh_from_db()
        self.assertTrue(announcement.is_read)
        self.assertEqual(announcement.status, read)

    def _make_evaluation_enrollment(self, student, suffix):
        from datetime import time

        teacher_person = m.Person.objects.create_user(
            username=f"evaluation-teacher-{suffix}",
            password="test-pass",
            first_name="استاد",
            last_name="ارزشیابی",
            email=f"evaluation-teacher-{suffix}@example.com",
            national_id=f"00000000{20 + int(suffix):02d}",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        teacher = m.Teacher.objects.create(
            person=teacher_person,
            teacher_code=f"T-EVAL-{suffix}",
            department=self.field.department,
            hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان آزمون",
            room_number=f"E{suffix}",
            capacity=30,
            classroom_type="کلاس",
        )
        lesson = m.Lesson.objects.create(
            lesson_code=f"L-EVAL-{suffix}",
            title="ساختمان داده‌ها",
            theory_units=3,
            department=self.field.department,
        )
        day = m.Constant.objects.create(
            category="day_of_week", code=f"evaluation-day-{suffix}", label="شنبه"
        )
        offering = m.CourseOffering.objects.create(
            lesson=lesson,
            term=self.term,
            teacher=teacher,
            capacity=30,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom=classroom,
            is_active=True,
        )
        status = m.Constant.objects.create(
            category="enrollment_status", code=f"evaluation-registered-{suffix}", label="ثبت‌شده"
        )
        return m.Enrollment.objects.create(
            student=student, offering=offering, status=status
        ), teacher_person

    def test_evaluation_form_uses_existing_survey_fields_and_persists_response(self):
        self.client.force_login(self.users[0])
        enrollment, teacher_person = self._make_evaluation_enrollment(self.students[0], "1")
        url = (
            f"/api/portal/pages/evaluation-form/?student_code=S0&term=T1"
            f"&enrollment={enrollment.pk}"
        )

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="evaluation-form-panel"', html)
        self.assertIn("ساختمان داده‌ها", html)
        self.assertIn(teacher_person.full_name, html)
        for name in ("overall_rating", "teaching_quality", "behavior"):
            self.assertIn(f'name="{name}"', html)
        self.assertIn("پاسخ‌ها محرمانه هستند", html)

        payload = {
            "enrollment": enrollment.pk,
            "overall_rating": 3,
            "teaching_quality": 4,
            "behavior": 2,
            "comment": "بازخورد اختیاری",
        }
        response = self.client.post(
            url, data=json.dumps(payload), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(f"enrollment={enrollment.pk}", response.json()["redirect"])
        survey = m.TeacherSurvey.objects.get(enrollment=enrollment)
        self.assertEqual(survey.overall_rating, 3)
        self.assertEqual(survey.teaching_quality, 4)
        self.assertEqual(survey.behavior, 2)
        self.assertEqual(survey.comment, "بازخورد اختیاری")

        submitted = self.client.get(url).json()["html"]
        self.assertIn("ارزشیابی نهایی ثبت شده است", submitted)
        self.assertNotIn('class="live-form evaluation-live-form"', submitted)
        self.assertIn("<dd>4</dd>", submitted)
        self.assertIn("<dd>2</dd>", submitted)

    def test_react_validation_response_keeps_form_errors_from_failed_save(self):
        from apps.core.frontend.views import PortalView

        self.client.force_login(self.users[0])
        enrollment, _ = self._make_evaluation_enrollment(self.students[0], "7")
        url = (
            f"/api/portal/pages/evaluation-form/?student_code=S0&term=T1"
            f"&enrollment={enrollment.pk}"
        )
        original_context = PortalView.context
        context_calls = 0

        def context_without_rebuilt_form(view, request, slug=None):
            nonlocal context_calls
            context = original_context(view, request, slug)
            context_calls += 1
            if request.method == "POST" and context_calls == 2:
                context["form"] = None
            return context

        with patch(
            "apps.core.frontend.miri.forms.SurveyForm.save",
            side_effect=ValidationError("ارزشیابی این درس قبلاً ثبت شده است."),
        ), patch.object(
            PortalView, "context", autospec=True, side_effect=context_without_rebuilt_form
        ):
            response = self.client.post(
                url,
                data=json.dumps({
                    "enrollment": enrollment.pk,
                    "overall_rating": 4,
                    "teaching_quality": 5,
                    "behavior": 3,
                    "comment": "ورودی حفظ‌شده",
                }),
                content_type="application/json",
                HTTP_ACCEPT="application/vnd.amoozeshyar.react+json",
            )

        self.assertEqual(response.status_code, 400)
        self.assertIsNotNone(response.json()["form"])
        self.assertIn(
            "ارزشیابی این درس قبلاً ثبت شده است.",
            response.json()["form"]["non_field_errors"],
        )
        self.assertEqual(
            next(
                field["value"] for field in response.json()["form"]["fields"]
                if field["name"] == "comment"
            ),
            "ورودی حفظ‌شده",
        )

    def test_evaluation_form_does_not_accept_another_students_enrollment(self):
        self.client.force_login(self.users[0])
        foreign_enrollment, _ = self._make_evaluation_enrollment(self.students[1], "2")
        url = "/api/portal/pages/evaluation-form/?student_code=S0&term=T1"

        response = self.client.post(
            url,
            data=json.dumps({
                "enrollment": foreign_enrollment.pk,
                "overall_rating": 5,
                "teaching_quality": 5,
                "behavior": 5,
                "comment": "",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertFalse(m.TeacherSurvey.objects.filter(enrollment=foreign_enrollment).exists())

    def test_evaluation_list_builds_completed_and_pending_rows_from_owned_surveys(self):
        self.client.force_login(self.users[0])
        completed, _ = self._make_evaluation_enrollment(self.students[0], "4")
        pending, _ = self._make_evaluation_enrollment(self.students[0], "5")
        foreign, _ = self._make_evaluation_enrollment(self.students[1], "6")
        m.TeacherSurvey.objects.create(
            enrollment=completed,
            overall_rating=4,
            teaching_quality=4,
            behavior=4,
        )

        response = self.client.get("/api/portal/pages/evaluation/?term=T1")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("2 درس ثبت‌شده", html)
        self.assertIn("1 ارزشیابی تکمیل‌شده", html)
        self.assertIn("schema فعلی فقط امتیاز کلی، کیفیت تدریس و رفتار استاد را ذخیره می‌کند", html)
        self.assertIn("پاسخ‌ها به ثبت‌نام دانشجو پیوند دارند و ناشناس بودن تضمین نشده است", html)
        self.assertIn(f"enrollment={pending.pk}", html)
        self.assertNotIn(f"enrollment={completed.pk}", html)
        self.assertNotIn(f"enrollment={foreign.pk}", html)

    def test_notifications_filter_by_owned_type_and_mark_only_owned_records_read(self):
        self.client.force_login(self.users[0])
        role = m.Role.objects.create(role_name="notification-test-role")
        own_account = m.UserAccount.objects.create(
            person=self.users[0], role=role,
            username="notification-test-own", password="unused",
        )
        other_account = m.UserAccount.objects.create(
            person=self.users[1], role=role,
            username="notification-test-other", password="unused",
        )
        grade_type = m.Constant.objects.create(
            category="notification_type", code="grade", label="نمره"
        )
        system_type = m.Constant.objects.create(
            category="notification_type", code="system", label="سیستمی"
        )
        grade_notice = m.Notification.objects.create(
            user=own_account, title="ثبت نمره", message="اعلان نمرهٔ خودم",
            notification_type=grade_type,
        )
        m.Notification.objects.create(
            user=own_account, title="اعلان سامانه", message="متن سامانه",
            notification_type=system_type,
        )
        other_notice = m.Notification.objects.create(
            user=other_account, title="اعلان حساب دیگر", message="نباید نمایش داده شود",
            notification_type=grade_type,
        )
        filtered_url = "/api/portal/pages/notifications/?notification_type=grade"

        response = self.client.get(filtered_url)

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("اعلان نمرهٔ خودم", html)
        self.assertNotIn("متن سامانه", html)
        self.assertNotIn("نباید نمایش داده شود", html)
        self.assertIn("نمره", html)
        self.assertIn("notification-filter", html)

        response = self.client.post(
            filtered_url,
            data=json.dumps({"notification_id": grade_notice.pk}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("notification_type=grade", response.json()["redirect"])
        grade_notice.refresh_from_db()
        other_notice.refresh_from_db()
        self.assertTrue(grade_notice.is_read)
        self.assertFalse(other_notice.is_read)

        response = self.client.post(
            filtered_url,
            data=json.dumps({"notification_id": other_notice.pk}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_settings_page_renders_only_profile_backed_preferences(self):
        self.client.force_login(self.users[0])
        m.Constant.objects.create(category="language", code="fa", label="فارسی")
        m.Constant.objects.create(category="language", code="en", label="English")

        response = self.client.get("/api/portal/pages/settings/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="settings-page"', html)
        self.assertIn('name="preferred_language"', html)
        self.assertIn("English", html)
        self.assertIn('name="email"', html)
        self.assertIn('name="is_notification_enabled"', html)
        self.assertIn('class="settings-channel-notice"', html)

    def test_settings_post_updates_only_the_logged_in_person(self):
        self.client.force_login(self.users[0])
        persian = m.Constant.objects.create(category="language", code="fa", label="فارسی")

        response = self.client.post(
            "/api/portal/pages/settings/",
            data=json.dumps({
                "email": "updated@example.com",
                "address": "نشانی جدید",
                "preferred_language": persian.pk,
                "is_notification_enabled": False,
                "person_id": self.users[1].pk,
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("/portal/settings/", response.json()["redirect"])
        self.assertIn("settings_saved=1", response.json()["redirect"])
        self.users[0].refresh_from_db()
        self.users[1].refresh_from_db()
        self.assertEqual(self.users[0].email, "updated@example.com")
        self.assertEqual(self.users[0].address, "نشانی جدید")
        self.assertEqual(self.users[0].preferred_language, persian)
        self.assertFalse(self.users[0].is_notification_enabled)
        self.assertEqual(self.users[1].email, "1@example.com")
        self.assertEqual(self.users[1].address, "")

        saved_page = self.client.get(
            "/api/portal/pages/settings/?settings_saved=1"
        )
        self.assertEqual(saved_page.status_code, 200)
        saved_html = saved_page.json()["html"]
        self.assertIn('class="settings-save-result"', saved_html)
        self.assertIn("تنظیمات در حساب شما ذخیره شد", saved_html)
        self.assertIn("ترجیح اعلان فقط ذخیره شده است", saved_html)

    def test_attendance_page_summarizes_sessions_by_active_course(self):
        from datetime import time

        self.client.force_login(self.users[0])
        day = m.Constant.objects.create(
            category="day_of_week", code="saturday", label="شنبه"
        )
        teacher_person = m.Person.objects.create_user(
            username="attendance-teacher",
            password="test-pass",
            first_name="استاد",
            last_name="حضور",
            email="attendance-teacher@example.com",
            national_id="0000000004",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
        )
        teacher = m.Teacher.objects.create(
            person=teacher_person,
            teacher_code="T-ATTENDANCE",
            department=self.field.department,
            hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان آزمون",
            room_number="۱۰۲",
            capacity=30,
            classroom_type="کلاس",
        )
        lesson = m.Lesson.objects.create(
            lesson_code="L-ATTENDANCE",
            title="درس حضور",
            theory_units=3,
            department=self.field.department,
        )
        offering = m.CourseOffering.objects.create(
            lesson=lesson,
            term=self.term,
            teacher=teacher,
            capacity=30,
            day_of_week=day,
            start_time=time(8, 0),
            end_time=time(10, 0),
            classroom=classroom,
            is_active=True,
        )
        enrollment_status = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="ثبت‌شده"
        )
        enrollment = m.Enrollment.objects.create(
            student=self.students[0], offering=offering, status=enrollment_status
        )
        recorder_role = m.Role.objects.create(role_name="ثبت‌کنندهٔ حضور")
        recorder = m.UserAccount.objects.create(
            person=teacher_person,
            role=recorder_role,
            username="attendance-recorder",
            password="unused",
        )
        present = m.Constant.objects.create(
            category="attendance_status", code="present", label="حاضر"
        )
        absent = m.Constant.objects.create(
            category="attendance_status", code="absent", label="غایب"
        )
        for number, status in ((1, present), (2, absent)):
            m.Attendance.objects.create(
                enrollment=enrollment,
                session_number=number,
                session_date=date(2026, 1, number),
                attendance_status=status,
                attendance_time=time(8, 0),
                description=status.label,
                recorded_by=recorder,
            )

        response = self.client.get("/api/portal/pages/attendance/?term=T1")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="attendance-metrics"', html)
        self.assertIn('data-attendance-total="2"', html)
        self.assertIn('data-attendance-absences="1"', html)
        self.assertIn('data-attendance-active-courses="1"', html)
        self.assertIn('class="attendance-table-panel"', html)
        self.assertIn("درس حضور", html)
        self.assertIn("جلسات ثبت‌شده", html)
        self.assertIn("ثبت‌شده", html)
        self.assertIn("ارتباط با استاد", html)

    def test_only_the_current_navigation_group_is_open(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/student-card/")
        details = re.findall(rb'<details class="nav-group"([^>]*)>', response.json()["html"].encode())
        opened = [attrs for attrs in details if re.search(rb"\bopen\b", attrs)]
        self.assertEqual(len(opened), 1)

    def test_academic_activities_use_a_real_profile_summary_and_link_grid(self):
        recorder_role = m.Role.objects.create(role_name="activity-recorder")
        recorder = m.UserAccount.objects.create(
            person=self.users[0], role=recorder_role, username="activity-recorder",
            password="unused",
        )
        change_type = m.Constant.objects.create(
            category="change_type", code="activity", label="فعالیت آموزشی"
        )
        m.EducationalChangeLog.objects.create(
            student=self.students[0], changed_by=recorder, change_type=change_type,
            description="رویداد متعلق به دانشجوی جاری",
        )
        m.EducationalChangeLog.objects.create(
            student=self.students[1], changed_by=recorder, change_type=change_type,
            description="رویداد خصوصی دانشجوی دیگر",
        )
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/academic-activities/")
        html = response.json()["html"]
        self.assertIn(self.users[0].full_name, html)
        self.assertIn("activity-summary-strip", html)
        self.assertIn("activity-links-grid", html)
        self.assertIn("واحدهای فعال", html)
        self.assertIn("رویداد متعلق به دانشجوی جاری", html)
        self.assertNotIn("رویداد خصوصی دانشجوی دیگر", html)
        for slug in ("schedule", "attendance", "exam-card", "calendar"):
            self.assertIn(f'href="/portal/{slug}/', html)

    def test_payments_do_not_leak_another_student(self):
        successful = m.Constant.objects.create(
            category="payment_status", code="successful", label="موفق"
        )
        failed = m.Constant.objects.create(
            category="payment_status", code="failed", label="ناموفق / لغو"
        )
        for i, student in enumerate(self.students):
            m.Payment.objects.create(student=student, term=self.term, amount=100+i,
                payment_date=timezone.now(), tracking_code=f"PRIVATE-{i}", status=successful)
        m.Payment.objects.create(
            student=self.students[0], term=self.term, amount=50,
            payment_date=timezone.now(), tracking_code="FAILED-OWN", status=failed,
        )
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/payments/")
        html = response.json()["html"]
        self.assertIn("finance-summary-strip", html)
        self.assertIn("finance-transactions-panel", html)
        self.assertIn("PRIVATE-0", html)
        self.assertNotIn("PRIVATE-1", html)
        self.assertIn("شرح در مدل پرداخت ثبت نشده", html)
        self.assertIn("FAILED-OWN", html)
        self.assertIn("ناموفق ثبت شده و در جمع پرداخت‌های موفق محاسبه نشده", html)
        self.assertIn("پرداخت موفق:</strong> 100 ریال", html)
        self.assertEqual(self.client.get("/api/portal/pages/payments/?student_code=S1").status_code, 403)

    def test_finance_pages_render_inside_one_portal_shell(self):
        self.client.force_login(self.users[0])

        for slug in ("payments", "secure-payment", "tuition"):
            with self.subTest(slug=slug):
                response = self.client.get(f"/api/portal/pages/{slug}/")
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json()["html"].count('class="portal-shell"'), 1)

    def test_tuition_summary_uses_successful_payments_and_real_debt_only(self):
        successful = m.Constant.objects.create(
            category="payment_status", code="successful", label="موفق"
        )
        failed = m.Constant.objects.create(
            category="payment_status", code="failed", label="ناموفق"
        )
        self.students[0].tuition_debt = 1_200
        self.students[0].save(update_fields=["tuition_debt"])
        m.Payment.objects.create(
            student=self.students[0], term=self.term, amount=300,
            payment_date=timezone.now(), tracking_code="TUITION-PAID", status=successful,
        )
        m.Payment.objects.create(
            student=self.students[0], term=self.term, amount=700,
            payment_date=timezone.now(), tracking_code="TUITION-FAILED", status=failed,
        )
        self.client.force_login(self.users[0])

        response = self.client.get("/api/portal/pages/tuition/?student_code=S0&term=T1")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("finance-summary-strip", html)
        self.assertIn("300 ریال", html)
        self.assertIn("1,200 ریال", html)
        self.assertNotIn("700 ریال", html)
        self.assertIn("تعرفه و ریزبدهی ثابت/متغیر در داده‌های فعلی موجود نیست", html)
        self.assertIn('href="/portal/secure-payment/', html)
        self.assertIn('href="/portal/payments/', html)

    def test_request_submission_assigns_owner_and_pending_on_server(self):
        self.client.force_login(self.users[0])
        response = self.client.post("/portal/requests/", {
            "service_request_kind": self.kind.pk, "service_request_data": "درخواست واقعی",
            "service_requester": self.students[1].pk, "service_decision_state": 999})
        self.assertEqual(response.status_code, 302)
        row = m.StudentServiceRequest.objects.get()
        self.assertEqual(row.service_requester, self.students[0])
        self.assertEqual(row.service_decision_state.code, "pending")
        self.assertIn(f"request_id={row.pk}", response.url)

        result = self.client.get(
            f"/api/portal/pages/requests/?student_code=S0&term=T1&request_id={row.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="operation-submission-result"', html)
        self.assertIn("درخواست دانشجویی ثبت شد", html)
        self.assertIn("ارسال به سامانهٔ دانشگاهی انجام نشده است", html)
        self.assertIn("شمارهٔ تماس و پیوست در مدل/API فعلی پشتیبانی نمی‌شوند", html)

        foreign_request = m.StudentServiceRequest.objects.create(
            service_requester=self.students[1], service_request_kind=self.kind,
            service_request_data="اطلاعات خصوصی پروندهٔ دیگر",
            service_decision_state=row.service_decision_state,
        )
        foreign_result = self.client.get(
            f"/api/portal/pages/requests/?student_code=S0&term=T1&request_id={foreign_request.pk}"
        )
        self.assertEqual(foreign_result.status_code, 200)
        self.assertNotIn('class="operation-submission-result"', foreign_result.json()["html"])

    def test_request_types_are_required_and_certificate_request_is_not_issuance(self):
        self.client.force_login(self.users[0])
        submissions = (
            ("internship", {
                "request_type": "", "company_name": "سازمان مقصد",
                "intern_start_date": "2026-12-10", "duration_hours": 40,
            }),
            ("requests", {
                "service_request_kind": "", "service_request_data": "درخواست واقعی",
            }),
            ("education-certificate", {
                "service_request_kind": "", "service_request_data": "درخواست گواهی",
            }),
        )

        for slug, payload in submissions:
            with self.subTest(slug=slug):
                response = self.client.post(
                    f"/api/portal/pages/{slug}/",
                    data=json.dumps(payload),
                    content_type="application/json",
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.json()["error"]["code"], "validation_error")
                self.assertIn("errorlist", response.json()["html"])

        self.assertEqual(m.Internship.objects.count(), 0)
        self.assertEqual(m.StudentServiceRequest.objects.count(), 0)

        certificate_type = m.Constant.objects.get(
            category="service_request_type", code="employment_certificate"
        )
        submitted = self.client.post(
            "/api/portal/pages/education-certificate/?student_code=S0&term=T1",
            data=json.dumps({
                "service_request_kind": certificate_type.pk,
                "service_request_data": "درخواست گواهی اشتغال",
            }),
            content_type="application/json",
        )
        self.assertEqual(submitted.status_code, 200)
        request_record = m.StudentServiceRequest.objects.get(
            service_requester=self.students[0], service_request_kind=certificate_type
        )
        self.assertIn(f"request_id={request_record.pk}", submitted.json()["redirect"])

        result = self.client.get(
            f"/api/portal/pages/education-certificate/?student_code=S0&term=T1&request_id={request_record.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="operation-submission-result"', html)
        self.assertIn("درخواست گواهی آموزشی ثبت شد", html)
        self.assertIn("گواهی رسمی صادر نشده است", html)
        self.assertIn("مخاطب، تعداد نسخه و روش تحویل", html)

    def test_graduation_certificate_page_uses_real_checks_without_fake_issuance(self):
        self.client.force_login(self.users[0])
        department = m.Department.objects.get(department_code="D")
        lesson = m.Lesson.objects.create(
            lesson_code="L-GRAD-CERT", title="درس چارت",
            theory_units=3, department=department,
        )
        m.Curriculum.objects.create(
            field=self.field, lesson=lesson, recommended_term=1,
            calculated_units=3, is_active=True,
        )
        self.students[0].passed_units = 88
        self.students[0].save(update_fields=["passed_units"])

        response = self.client.get(
            "/api/portal/pages/graduation-certificate/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn("graduation-certificate-workflow", html)
        self.assertIn("88 واحد", html)
        self.assertIn("واحدهای چارت فعال", html)
        self.assertIn("3 واحد", html)
        self.assertIn("تسویهٔ کتابخانه در این نسخه قابل بررسی نیست", html)
        self.assertIn("صدور رسمی به سرویس متصل نیاز دارد", html)
        self.assertIn('href="/portal/graduation/', html)
        self.assertIn('href="/portal/curriculum/', html)
        self.assertNotIn("فرم درخواست صدور", html)
        self.assertNotIn("گواهی دانش‌آموختگی صادر شد", html)

    def test_no_student_profile_has_explicit_empty_state(self):
        self.client.force_login(self.users[0])
        m.Student.objects.filter(pk=self.students[0].pk).delete()
        response = self.client.get("/api/portal/pages/home/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("پروندهٔ دانشجویی", response.json()["html"])

    def test_section_breadcrumb_uses_persian_labels(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/transcript/")

        self.assertEqual(response.status_code, 200)
        self.assertIn('aria-label="مسیر صفحه"', response.json()["html"])
        self.assertIn("داشبورد", response.json()["html"])
        self.assertNotIn("????", response.json()["html"])

    def test_guide_contains_actionable_instructions_and_real_page_links(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/guide/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertEqual(html.count('class="guide-topic"'), 4)
        self.assertIn("چطور انتخاب واحد کنم؟", html)
        self.assertIn("چرا ثبت‌نام مسدود است؟", html)
        self.assertIn("حذف اضطراری چه محدودیتی دارد؟", html)
        self.assertIn("اعلان و پیام استاد را کجا ببینیم؟", html)
        self.assertIn("علت انسداد را به‌صورت مستقل گزارش نمی‌کند", html)
        self.assertIn("API فعلی حذف اضطراری حداقل واحد را کنترل نمی‌کند", html)
        self.assertIn('href="/portal/enrollment/', html)
        self.assertIn('href="/portal/registration-status/', html)
        self.assertIn('href="/portal/emergency-drop/', html)
        self.assertIn('href="/portal/announcements/', html)
        self.assertIn('href="/portal/support/', html)

    def test_support_page_lists_owned_root_tickets_and_their_latest_reply(self):
        self.client.force_login(self.users[0])
        category = m.TicketCategory.objects.create(name="پشتیبانی آزمایشی")
        own_ticket = m.Ticket.objects.create(
            creator=self.users[0], category=category,
            subject="پیگیری تیکت خودم", content="شرح تیکت",
        )
        m.Ticket.objects.create(
            creator=self.users[1], category=category,
            subject="تیکت حساب دیگر", content="نباید نمایش داده شود",
        )
        m.Ticket.objects.create(
            creator=self.users[1], category=category, parent=own_ticket,
            subject="پاسخ تیکت", content="پاسخ واقعی پشتیبانی",
        )

        response = self.client.get("/api/portal/pages/support/")

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('class="support-form-panel"', html)
        self.assertIn('class="data-table support-ticket-list"', html)
        self.assertIn("پیگیری تیکت خودم", html)
        self.assertIn("پاسخ واقعی پشتیبانی", html)
        self.assertNotIn("تیکت حساب دیگر", html)
        self.assertIn("بارگذاری فایل در این نسخه پشتیبانی نمی‌شود", html)

    def test_support_submission_uses_the_active_open_status(self):
        self.client.force_login(self.users[0])
        category = m.TicketCategory.objects.create(name="پشتیبانی آزمایشی")
        open_status = m.Constant.objects.create(
            category="ticket_status", code="open", label="باز", is_active=True,
        )

        response = self.client.post(
            "/api/portal/pages/support/",
            data=json.dumps({
                "category": category.pk,
                "subject": "ثبت تیکت جدید",
                "content": "شرح مشکل",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        ticket = m.Ticket.objects.get(subject="ثبت تیکت جدید")
        self.assertIn(f"request_id={ticket.pk}", response.json()["redirect"])
        self.assertEqual(ticket.creator, self.users[0])
        self.assertEqual(ticket.status, open_status)

        result_response = self.client.get(
            f"/api/portal/pages/support/?student_code=S0&term=T1&request_id={ticket.pk}"
        )
        self.assertEqual(result_response.status_code, 200)
        result_html = result_response.json()["html"]
        self.assertIn('id="support-submission-result"', result_html)
        self.assertIn(ticket.subject, result_html)
        self.assertIn(open_status.label, result_html)
        self.assertIn("فایل پیوست نشده", result_html)

        foreign_ticket = m.Ticket.objects.create(
            creator=self.users[1], category=category,
            subject="تیکت خصوصی حساب دیگر", content="شرح خصوصی",
            status=open_status,
        )
        foreign_result = self.client.get(
            f"/api/portal/pages/support/?student_code=S0&term=T1&request_id={foreign_ticket.pk}"
        ).json()["html"]
        self.assertNotIn('id="support-submission-result"', foreign_result)

    def test_payment_page_does_not_fake_a_gateway(self):
        self.students[0].tuition_debt = 1_200_000
        self.students[0].save(update_fields=["tuition_debt"])
        self.client.force_login(self.users[0])
        response = self.client.get("/api/portal/pages/secure-payment/")
        html = response.json()["html"]
        self.assertIn("درگاه", html)
        self.assertIn("finance-debt-panel", html)
        self.assertIn("finance-payment-review", html)
        self.assertIn(self.users[0].full_name, html)
        self.assertIn("1,200,000 ریال", html)
        self.assertIn('disabled aria-disabled="true"', html)
        self.assertIn('href="/portal/payments/', html)
        self.assertNotIn('name="card_number"', html)
        self.assertEqual(m.Payment.objects.count(), 0)

    def test_portal_page_api_returns_database_backed_html_and_profile_metadata(self):
        self.client.force_login(self.users[0])

        response = self.client.get("/api/portal/pages/transcript/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["page"], "transcript")
        self.assertEqual(response.json()["profile"]["student_code"], "S0")
        self.assertIn(self.users[0].full_name, response.json()["html"])
        self.assertIn('class="portal-shell"', response.json()["html"])

    def test_transcript_shows_current_enrollments_without_inventing_split_grades(self):
        from datetime import time

        department = m.Department.objects.get(department_code="D")
        teacher = m.Teacher.objects.create(
            person=self.users[1], teacher_code="T-TRANSCRIPT",
            department=department, hire_date=date(2010, 1, 1),
        )
        classroom = m.Classroom.objects.create(
            building_name="ساختمان کارنامه", room_number="۲۰۱",
            capacity=30, classroom_type="کلاس",
        )
        registered = m.Constant.objects.create(
            category="enrollment_status", code="registered", label="در حال گذراندن"
        )
        scored_lesson = m.Lesson.objects.create(
            lesson_code="L-TRANSCRIPT-1", title="درس دارای نمره",
            theory_units=3, practical_units=0, department=department,
        )
        unscored_lesson = m.Lesson.objects.create(
            lesson_code="L-TRANSCRIPT-2", title="درس بدون نمره",
            theory_units=2, practical_units=0, department=department,
        )
        for index, lesson in enumerate((scored_lesson, unscored_lesson)):
            offering = m.CourseOffering.objects.create(
                lesson=lesson, term=self.term, teacher=teacher, capacity=30,
                start_time=time(8 + index * 2, 0), end_time=time(10 + index * 2, 0),
                classroom=classroom,
            )
            enrollment = m.Enrollment.objects.create(
                student=self.students[0], offering=offering, status=registered,
            )
            if index == 0:
                m.Grade.objects.create(enrollment=enrollment, score="18.50")

        foreign_lesson = m.Lesson.objects.create(
            lesson_code="L-TRANSCRIPT-PRIVATE", title="درس خصوصی پروندهٔ دیگر",
            theory_units=4, practical_units=0, department=department,
        )
        foreign_offering = m.CourseOffering.objects.create(
            lesson=foreign_lesson, term=self.term, teacher=teacher, capacity=30,
            start_time=time(14, 0), end_time=time(16, 0), classroom=classroom,
        )
        m.Enrollment.objects.create(
            student=self.students[1], offering=foreign_offering, status=registered,
        )
        self.students[0].total_gpa = "17.25"
        self.students[0].passed_units = 88
        self.students[0].save(update_fields=["total_gpa", "passed_units"])
        self.client.force_login(self.users[0])

        response = self.client.get(
            "/api/portal/pages/transcript/?student_code=S0&term=T1"
        )

        self.assertEqual(response.status_code, 200)
        html = response.json()["html"]
        self.assertIn('data-current-units="5"', html)
        self.assertIn("درس دارای نمره", html)
        self.assertIn("درس بدون نمره", html)
        self.assertIn("18.50", html)
        self.assertIn("نمرهٔ ثبت‌شده", html)
        self.assertIn("مدل نمره میان‌ترم و پایان‌ترم را جدا نمی‌کند", html)
        self.assertNotIn("درس خصوصی پروندهٔ دیگر", html)
        self.assertNotIn("نمرهٔ میان‌ترم", html)
        self.assertNotIn("نمرهٔ پایان‌ترم", html)
        self.assertIn('href="/portal/grade-appeal/', html)
        self.assertIn('href="/portal/curriculum/', html)

    def test_portal_page_api_returns_json_authentication_error(self):
        response = self.client.get("/api/portal/pages/transcript/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "authentication_required")

    def test_portal_page_api_keeps_student_profiles_scoped(self):
        self.client.force_login(self.users[0])

        response = self.client.get("/api/portal/pages/transcript/?student_code=S1")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"]["code"], "permission_denied")

    def test_portal_page_api_returns_bound_form_errors_as_json(self):
        self.client.force_login(self.users[0])

        response = self.client.post(
            "/api/portal/pages/financial-aid/?student_code=S0&term=T1",
            data=json.dumps({"scholarship_type": "", "scholarship_reason": "درخواست واقعی"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"]["code"], "validation_error")
        self.assertIn("درخواست واقعی", response.json()["html"])
        self.assertIn("errorlist", response.json()["html"])

    def test_portal_page_api_submits_valid_existing_form(self):
        self.client.force_login(self.users[0])

        response = self.client.post(
            "/api/portal/pages/financial-aid/?student_code=S0&term=T1",
            data=json.dumps({"scholarship_type": "وام", "scholarship_reason": "درخواست واقعی"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        application = m.ScholarshipApplication.objects.get(
            scholarship_applicant=self.students[0], scholarship_type="وام"
        )
        self.assertIn(f"request_id={application.pk}", response.json()["redirect"])

        result = self.client.get(
            f"/api/portal/pages/financial-aid/?student_code=S0&term=T1&request_id={application.pk}"
        )
        self.assertEqual(result.status_code, 200)
        html = result.json()["html"]
        self.assertIn('class="operation-submission-result"', html)
        self.assertIn("درخواست تسهیلات ثبت شد", html)
        self.assertIn("در انتظار", html)
        self.assertIn("مبلغ درخواستی، شمارهٔ شبا و پیوست", html)
        self.assertIn("ثبت درخواست به معنی تأیید یا پرداخت نیست", html)
        self.assertNotIn('name="scholarship_amount"', html)
        self.assertNotIn('name="iban"', html)
        self.assertNotIn('name="attachment"', html)
        self.assertIn("تخصیص یا تأیید نهایی وام نیست", html)


@tag("seeded_frontend")
class SeededFrontendSmokeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Execute the user's root seed only inside Django's temporary test database.
        import seed_data
        with redirect_stdout(StringIO()):
            seed_data.run()

    def test_seeded_student_can_render_every_owned_page(self):
        from apps.core.frontend.registry import PAGES
        student_user = m.Person.objects.get(username="student1")
        student = m.Student.objects.get(person=student_user)
        self.client.force_login(student_user)
        response = self.client.get("/api/portal/pages/home/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(student_user.full_name, response.json()["html"])
        for slug in PAGES:
            response = self.client.get(f"/api/portal/pages/{slug}/")
            self.assertEqual(response.status_code, 200, slug)

        enrollment = m.Enrollment.objects.filter(
            student=student, offering__term__is_active=True
        ).select_related("offering__lesson").first()
        self.assertIsNotNone(enrollment)
        student_card = self.client.get("/api/portal/pages/student-card/").json()["html"]
        exam_card = self.client.get("/api/portal/pages/exam-card/").json()["html"]
        self.assertIn(student.student_code, student_card)
        self.assertIn(enrollment.offering.lesson.title, exam_card)

    def test_seeded_student_can_submit_owned_requests(self):
        student_user = m.Person.objects.get(username="student1")
        student = m.Student.objects.get(person=student_user)
        self.client.force_login(student_user)
        term = m.Term.objects.get(is_active=True)
        enrollment = m.Enrollment.objects.filter(
            student=student, offering__term=term, grades__score__isnull=False
        ).distinct().first()
        self.assertIsNotNone(enrollment)
        response = self.client.post("/portal/grade-appeal/", {
            "enrollment": enrollment.pk, "appeal_reason": "بررسی مجدد نمره"})
        self.assertEqual(response.status_code, 302)
        appeal = m.GradeAppeal.objects.get(enrollment=enrollment)
        self.assertEqual(appeal.appeal_status.code, "pending")
        self.assertIn(f"request_id={appeal.pk}", response.url)
        appeal_result = self.client.get(
            f"/api/portal/pages/grade-appeal/?student_code={student.student_code}"
            f"&term={term.term_code}&request_id={appeal.pk}"
        )
        self.assertEqual(appeal_result.status_code, 200)
        appeal_html = appeal_result.json()["html"]
        self.assertIn('class="operation-submission-result"', appeal_html)
        self.assertIn("مهلت مجاز اعتراض در مدل/API فعلی بررسی نمی‌شود", appeal_html)
        self.assertIn("فرم امکان پیوست فایل ندارد", appeal_html)
        self.assertIn("اعتراض به نمره", appeal_html)
        self.assertIn("در انتظار", appeal_html)
        self.assertIn("درخواست برای رسیدگی ثبت شده است", appeal_html)

        response = self.client.post("/portal/guest-request/", {"destination_university": "دانشگاه مقصد"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(m.TransferRequest.objects.filter(student=student, destination_university="دانشگاه مقصد").exists())

        # No graduation-request lookup/workflow is defined in the current seed.
        # The read-only audit page must not accept an unrelated certificate type.
        service_request_count = m.StudentServiceRequest.objects.filter(
            service_requester=student
        ).count()
        response = self.client.post("/portal/graduation/", {
            "service_request_data": "پرونده فارغ‌التحصیلی"})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            m.StudentServiceRequest.objects.filter(service_requester=student).count(),
            service_request_count,
        )

        response = self.client.post("/portal/financial-aid/", {
            "scholarship_type": "وام", "scholarship_reason": "درخواست تسهیلات"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(m.ScholarshipApplication.objects.get(scholarship_applicant=student).scholarship_status.code, "pending")

        internship_type = m.Constant.objects.filter(category="internship_request_type", is_active=True).first()
        response = self.client.post("/portal/internship/", {
            "request_type": internship_type.pk, "company_name": "سازمان مقصد",
            "intern_start_date": "2026-12-10", "duration_hours": 40})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(m.Internship.objects.filter(student=student, company_name="سازمان مقصد", duration_hours=40).exists())

"""آزمون جریان واقعی صفحه‌ها روی دیتابیس تست مستقل از دیتابیس محلی."""
from datetime import date, timedelta
from contextlib import redirect_stdout
from io import StringIO
from django.test import TestCase
from django.test import SimpleTestCase
from django.test import tag
from django.utils import timezone
from apps.core import models as m
import re


class FrontendTeamStructureTests(SimpleTestCase):
    def test_team_manifests_cover_each_portal_page_once(self):
        from apps.core.frontend.registry import GROUPS, PAGES

        self.assertEqual(len(GROUPS), 5)
        declared = []
        for owner, (_, module) in GROUPS.items():
            self.assertTrue(hasattr(module, "PAGES"), f"{owner} must declare its pages")
            declared.extend(module.PAGES)

        self.assertEqual(len(declared), len(set(declared)), "a page has more than one owner")
        self.assertEqual(set(declared), set(PAGES))

    def test_frontend_lead_and_special_pages_are_explicit(self):
        from apps.core.frontend.registry import GROUPS
        from apps.core.frontend.mobina import SPECIAL_PAGES
        from apps.core.frontend.neyousha_pouya import COMPONENTS
        from apps.core.frontend.academic_services import MEMBER_PAGES

        self.assertEqual(GROUPS["neyousha_pouya"][0], "پویا و نیوشا (لید فرانت)")
        self.assertEqual(set(SPECIAL_PAGES), {"login", "dashboard"})
        self.assertIn("term_picker", COMPONENTS)
        self.assertEqual(set(MEMBER_PAGES), {"shahsavand", "omid"})
        self.assertEqual(len(MEMBER_PAGES["shahsavand"]), 5)
        self.assertEqual(len(MEMBER_PAGES["omid"]), 10)


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

    def test_anonymous_pages_require_login(self):
        self.assertEqual(self.client.get("/").status_code, 302)
        self.assertEqual(self.client.get("/portal/payments/").status_code, 302)
        self.assertEqual(self.client.get("/login/").status_code, 200)

    def test_all_pages_render_without_demo_person(self):
        from apps.core.frontend.registry import PAGES, GROUPS
        self.assertEqual(len(GROUPS), 5)
        self.client.force_login(self.users[0])
        for slug in PAGES:
            response = self.client.get(f"/portal/{slug}/")
            self.assertEqual(response.status_code, 200, slug)
            self.assertNotContains(response, "ali.mohammadi@example.edu")
        self.assertContains(self.client.get("/"), "دانشجو0")

    def test_student_and_exam_cards_use_page_specific_real_data_templates(self):
        self.client.force_login(self.users[0])

        student_card = self.client.get("/portal/student-card/")
        self.assertContains(student_card, 'class="digital-card"')
        self.assertContains(student_card, self.users[0].full_name)
        self.assertContains(student_card, "S0")
        self.assertNotContains(student_card, "23456789")

        exam_card = self.client.get("/portal/exam-card/")
        self.assertContains(exam_card, "exam-card-student")
        self.assertContains(exam_card, "exam-card-table")
        self.assertContains(exam_card, "صدور کارت رسمی در دسترس نیست")
        self.assertNotContains(exam_card, "data-demo-action")
        self.assertNotContains(exam_card, "سالن ۱")

    def test_only_the_current_navigation_group_is_open(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/portal/student-card/")
        details = re.findall(rb'<details class="nav-group"([^>]*)>', response.content)
        opened = [attrs for attrs in details if re.search(rb"\bopen\b", attrs)]
        self.assertEqual(len(opened), 1)

    def test_academic_activities_use_a_real_profile_summary_and_link_grid(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/portal/academic-activities/")
        self.assertContains(response, self.users[0].full_name)
        self.assertContains(response, "activity-summary-strip")
        self.assertContains(response, "activity-links-grid")
        self.assertContains(response, "واحدهای فعال")

    def test_payments_do_not_leak_another_student(self):
        for i, student in enumerate(self.students):
            m.Payment.objects.create(student=student, term=self.term, amount=100+i,
                payment_date=timezone.now(), tracking_code=f"PRIVATE-{i}")
        self.client.force_login(self.users[0])
        response = self.client.get("/portal/payments/")
        self.assertContains(response, "finance-summary-strip")
        self.assertContains(response, "finance-transactions-panel")
        self.assertContains(response, "PRIVATE-0")
        self.assertNotContains(response, "PRIVATE-1")
        self.assertEqual(self.client.get("/portal/payments/?student_code=S1").status_code, 403)

    def test_request_submission_assigns_owner_and_pending_on_server(self):
        self.client.force_login(self.users[0])
        response = self.client.post("/portal/requests/", {
            "service_request_kind": self.kind.pk, "service_request_data": "درخواست واقعی",
            "service_requester": self.students[1].pk, "service_decision_state": 999})
        self.assertEqual(response.status_code, 302)
        row = m.StudentServiceRequest.objects.get()
        self.assertEqual(row.service_requester, self.students[0])
        self.assertEqual(row.service_decision_state.code, "pending")

    def test_no_student_profile_has_explicit_empty_state(self):
        self.client.force_login(self.users[0])
        m.Student.objects.filter(pk=self.students[0].pk).delete()
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "پروندهٔ دانشجویی")

    def test_section_breadcrumb_uses_persian_labels(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/portal/transcript/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'aria-label="مسیر صفحه"')
        self.assertContains(response, "داشبورد")
        self.assertNotContains(response, "????")

    def test_payment_page_does_not_fake_a_gateway(self):
        self.client.force_login(self.users[0])
        response = self.client.get("/portal/secure-payment/")
        self.assertContains(response, "درگاه")
        self.assertContains(response, "finance-debt-panel")
        self.assertEqual(m.Payment.objects.count(), 0)


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
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, student_user.full_name)
        for slug in PAGES:
            response = self.client.get(f"/portal/{slug}/")
            self.assertEqual(response.status_code, 200, slug)

        enrollment = m.Enrollment.objects.filter(
            student=student, offering__term__is_active=True
        ).select_related("offering__lesson").first()
        self.assertIsNotNone(enrollment)
        self.assertContains(self.client.get("/portal/student-card/"), student.student_code)
        self.assertContains(
            self.client.get("/portal/exam-card/"), enrollment.offering.lesson.title
        )

    def test_seeded_student_can_submit_owned_requests(self):
        student_user = m.Person.objects.get(username="student1")
        student = m.Student.objects.get(person=student_user)
        self.client.force_login(student_user)
        term = m.Term.objects.get(is_active=True)
        enrollment = m.Enrollment.objects.filter(student=student, offering__term=term).first()
        self.assertIsNotNone(enrollment)
        response = self.client.post("/portal/grade-appeal/", {
            "enrollment": enrollment.pk, "appeal_reason": "بررسی مجدد نمره"})
        self.assertEqual(response.status_code, 302)
        appeal = m.GradeAppeal.objects.get(enrollment=enrollment)
        self.assertEqual(appeal.appeal_status.code, "pending")

        response = self.client.post("/portal/guest-request/", {"destination_university": "دانشگاه مقصد"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(m.TransferRequest.objects.filter(student=student, destination_university="دانشگاه مقصد").exists())

        service_kind = m.Constant.objects.get(category="service_request_type", code="certificate")
        response = self.client.post("/portal/graduation/", {
            "service_request_kind": service_kind.pk, "service_request_data": "پرونده فارغ‌التحصیلی"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(m.StudentServiceRequest.objects.filter(
            service_requester=student, service_request_data__contains="فارغ‌التحصیلی").exists())

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

import importlib
from datetime import date

from django.test import TestCase

from apps.core import api
from apps.core.models import (
    Constant,
    Department,
    Faculty,
    Field,
    Person,
    Role,
    ScholarshipApplication,
    Student,
    StudentServiceRequest,
    UserAccount,
)


# SDD §5 requests: #10 FUFD03, #22 FUDO02, #24 FUFP04, #25 FUFP05, #26 FUFP06.
# ADR-004 defines the shared workflow shape because the behavioral source is absent.
class RequestWorkflowFixtures(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.statuses = {}
        for category, code, label in (
            ("review_status", "pending", "در انتظار بررسی"),
            ("review_status", "approved", "تأیید"),
            ("review_status", "rejected", "رد"),
            ("educational_level", "bachelor", "کارشناسی"),
            ("student_status", "active", "فعال"),
            ("service_request_type", "installment", "تقسیط"),
        ):
            cls.statuses[(category, code)] = Constant.objects.get_or_create(
                category=category,
                code=code,
                defaults={"label": label},
            )[0]
        for code in ("submitted", "in_review"):
            cls.statuses[("review_status", code)] = Constant.objects.get(
                category="review_status", code=code
            )

        faculty = Faculty.objects.create(faculty_name="دانشکده درخواست", faculty_code="REQ")
        department = Department.objects.create(
            faculty=faculty,
            department_name="گروه درخواست",
            department_code="REQ",
        )
        field = Field.objects.create(
            department=department,
            field_name="رشته درخواست",
            field_code="REQ",
        )
        cls.student_person = Person.objects.create_user(
            username="request-student",
            password="Person@Password1",
            first_name="دانشجوی",
            last_name="درخواست",
            email="request-student@example.com",
            national_id="0080000001",
            birth_date=date(2001, 1, 1),
            birth_place="تهران",
        )
        student = Student.objects.create(
            person=cls.student_person,
            student_code="RQ-001",
            educational_level=cls.statuses[("educational_level", "bachelor")],
            field=field,
            application_date=date(2022, 9, 23),
            status=cls.statuses[("student_status", "active")],
        )
        cls.request = StudentServiceRequest.objects.create(
            service_requester=student,
            service_request_kind=cls.statuses[("service_request_type", "installment")],
            service_request_data="درخواست نمونه",
            service_decision_state=cls.statuses[("review_status", "submitted")],
        )

        cls.education_role = Role.objects.create(role_name="education officer")
        cls.education_reviewer = Person.objects.create_user(
            username="education-reviewer",
            password="Person@Password1",
            first_name="کارشناس",
            last_name="آموزش",
            email="education-reviewer@example.com",
            national_id="0080000002",
            birth_date=date(1980, 1, 1),
            birth_place="شیراز",
        )
        UserAccount.objects.create(
            person=cls.education_reviewer,
            role=cls.education_role,
            username="education-reviewer-account",
            password="unused",
        )
        cls.scholarship_role = Role.objects.create(role_name="scholarship officer")

    def status(self, category, code):
        return self.statuses[(category, code)]

    def service(self):
        try:
            return importlib.import_module("apps.core.requests.services")
        except ModuleNotFoundError:
            self.fail("apps.core.requests.services is not implemented")


class RequestWorkflowServiceTests(RequestWorkflowFixtures):
    def test_submitted_request_moves_to_review_and_then_a_decision(self):
        service = self.service()

        reviewing = service.transition_request(
            self.request, "in_review", reviewer=self.education_reviewer
        )
        self.assertEqual(reviewing.service_decision_state.code, "in_review")

        approved = service.transition_request(
            reviewing, "approved", reviewer=self.education_reviewer
        )
        approved.refresh_from_db()
        self.assertEqual(approved.service_decision_state.code, "approved")

    def test_legacy_pending_can_enter_review(self):
        self.request.service_decision_state = self.status("review_status", "pending")
        self.request.save(update_fields=["service_decision_state"])

        updated = self.service().transition_request(
            self.request, "in_review", reviewer=self.education_reviewer
        )

        self.assertEqual(updated.service_decision_state.code, "in_review")

    def test_invalid_transitions_and_targets_are_rejected(self):
        service = self.service()
        self.request.service_decision_state = self.status("review_status", "approved")
        self.request.save(update_fields=["service_decision_state"])

        with self.assertRaises(api.APIError) as invalid_transition:
            service.transition_request(
                self.request, "rejected", reviewer=self.education_reviewer
            )
        self.assertEqual(invalid_transition.exception.code, "invalid_transition")

        with self.assertRaises(api.APIError) as invalid_target:
            service.transition_request(
                self.request, "cancelled", reviewer=self.education_reviewer
            )
        self.assertEqual(invalid_target.exception.code, "invalid_transition")

        self.request.service_decision_state = self.status("review_status", "submitted")
        self.request.save(update_fields=["service_decision_state"])
        with self.assertRaises(api.APIError) as bypassed_review:
            service.transition_request(
                self.request, "approved", reviewer=self.education_reviewer
            )
        self.assertEqual(bypassed_review.exception.code, "invalid_transition")

    def test_review_requires_a_role_allowed_for_that_request_type(self):
        service = self.service()

        with self.assertRaises(api.APIError) as denied:
            service.transition_request(
                self.request, "in_review", reviewer=self.student_person
            )

        self.assertEqual(denied.exception.code, "permission_denied")

    def test_missing_target_status_constant_is_a_clear_configuration_error(self):
        Constant.objects.get(category="review_status", code="in_review").delete()

        with self.assertRaises(api.APIError) as missing:
            self.service().transition_request(
                self.request, "in_review", reviewer=self.education_reviewer
            )

        self.assertEqual(missing.exception.code, "request_status_unavailable")

    def test_registry_includes_only_existing_request_models(self):
        registry = self.service().REQUEST_MODELS

        self.assertIn("student-service", registry)
        self.assertIn("scholarship-application", registry)
        self.assertIn("grade-appeal", registry)
        self.assertIn("thesis-progress-report", registry)
        for definition in registry.values():
            self.assertTrue(hasattr(definition.model, definition.status_field))

    def test_migration_provides_all_transition_targets_for_each_status_category(self):
        for category in (
            "review_status",
            "proposal_status",
            "appeal_status",
            "thesis_review_status",
        ):
            codes = set(
                Constant.objects.filter(category=category).values_list("code", flat=True)
            )
            self.assertTrue({"submitted", "in_review", "approved", "rejected"} <= codes)

    def test_scholarship_requests_require_the_scholarship_reviewer_role(self):
        scholarship = ScholarshipApplication.objects.create(
            scholarship_applicant=self.request.service_requester,
            scholarship_type="merit",
            scholarship_reason="درخواست نمونه",
            scholarship_status=self.status("review_status", "submitted"),
        )

        with self.assertRaises(api.APIError) as denied:
            self.service().transition_request(
                scholarship, "in_review", reviewer=self.education_reviewer
            )

        self.assertEqual(denied.exception.code, "permission_denied")


class RequestWorkflowAPITests(RequestWorkflowFixtures):
    def test_authenticated_reviewer_can_transition_a_request(self):
        self.client.force_login(self.education_reviewer)

        response = self.client.post(
            f"/api/requests/student-service/{self.request.pk}/review/",
            data='{"target_status":"in_review"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["request"]["status"], "in_review")

    def test_review_endpoint_requires_authentication_and_valid_json(self):
        path = f"/api/requests/student-service/{self.request.pk}/review/"

        unauthenticated = self.client.post(path, data='{"target_status":"in_review"}', content_type="application/json")
        self.assertEqual(unauthenticated.status_code, 401)

        self.client.force_login(self.education_reviewer)
        invalid_json = self.client.post(path, data="{", content_type="application/json")
        self.assertEqual(invalid_json.status_code, 400)
        self.assertEqual(invalid_json.json()["error"]["code"], "invalid_json")

    def test_unknown_request_type_returns_not_found(self):
        self.client.force_login(self.education_reviewer)

        response = self.client.post(
            "/api/requests/not-a-request/1/review/",
            data='{"target_status":"in_review"}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["error"]["code"], "request_type_not_found")

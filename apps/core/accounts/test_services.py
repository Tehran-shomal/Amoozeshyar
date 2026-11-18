import importlib
import json
from datetime import date, timedelta

from django.conf import settings
from django.http import JsonResponse
from django.test import RequestFactory, TestCase
from django.utils import timezone

from apps.core import api
from apps.core.models import (
    Constant,
    Department,
    Faculty,
    Field,
    Person,
    Role,
    Student,
    UserAccount,
)


class AccountServiceTests(TestCase):
    # FUIP09, #85 FUSP07, #126 NFSP11, #129 FUOP16, and #140 NFSP13.
    @classmethod
    def setUpTestData(cls):
        cls.person = Person.objects.create_user(
            username="sara",
            password="Person@Password1",
            first_name="سارا",
            last_name="آزمون",
            email="sara@example.com",
            national_id="0012345678",
            birth_date=date(2001, 1, 1),
            birth_place="تهران",
        )
        cls.student_role = Role.objects.create(role_name="دانشجو")
        cls.teacher_role = Role.objects.create(role_name="استاد")
        cls.account = UserAccount.objects.create(
            person=cls.person,
            role=cls.student_role,
            username="student-alias",
            password="legacy-value-must-not-authenticate",
        )

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
        cls.bachelor = Constant.objects.create(
            category="educational_level",
            code="bachelor",
            label="کارشناسی",
        )
        cls.master = Constant.objects.create(
            category="educational_level",
            code="master",
            label="ارشد",
        )

    def service(self):
        try:
            return importlib.import_module("apps.core.accounts.services")
        except ModuleNotFoundError:
            self.fail("apps.core.accounts.services is not implemented")

    def function(self, name):
        function = getattr(self.service(), name, None)
        self.assertTrue(callable(function), f"{name} is not implemented")
        return function

    def create_student(self, code, level):
        return Student.objects.create(
            person=self.person,
            student_code=code,
            educational_level=level,
            field=self.field,
            application_date=date(2022, 9, 23),
        )

    def test_successful_login_uses_person_password_and_updates_account(self):
        authenticate_person = self.function("authenticate_person")

        user = authenticate_person("sara", "Person@Password1", request=None)

        self.assertEqual(user, self.person)
        self.account.refresh_from_db()
        self.assertEqual(self.account.failed_login_count, 0)
        self.assertIsNone(self.account.locked_until)
        self.assertIsNotNone(self.account.last_login_at)
        self.assertIsNotNone(self.account.last_activity_at)

    def test_invalid_credentials_increment_the_linked_account(self):
        authenticate_person = self.function("authenticate_person")

        self.assertIsNone(authenticate_person("sara", "wrong", request=None))

        self.account.refresh_from_db()
        self.assertEqual(self.account.failed_login_count, 1)
        self.assertIsNone(self.account.locked_until)

    def test_non_superuser_without_a_role_account_cannot_log_in(self):
        authenticate_person = self.function("authenticate_person")
        Person.objects.create_user(
            username="unlinked",
            password="Person@Password1",
            first_name="بدون",
            last_name="نقش",
            email="unlinked@example.com",
            national_id="0087654321",
            birth_date=date(2000, 1, 1),
            birth_place="تهران",
        )

        user = authenticate_person("unlinked", "Person@Password1", request=None)

        self.assertIsNone(user)

    def test_fifth_failed_login_locks_the_account(self):
        authenticate_person = self.function("authenticate_person")

        for _ in range(4):
            self.assertIsNone(authenticate_person("sara", "wrong", request=None))
        with self.assertRaises(api.APIError) as raised:
            authenticate_person("sara", "wrong", request=None)

        self.assertEqual(raised.exception.code, "account_locked")
        self.account.refresh_from_db()
        self.assertEqual(self.account.failed_login_count, 5)
        self.assertGreater(self.account.locked_until, timezone.now())

    def test_locked_account_is_rejected_even_with_the_correct_password(self):
        authenticate_person = self.function("authenticate_person")
        self.account.locked_until = timezone.now() + timedelta(minutes=5)
        self.account.save(update_fields=["locked_until"])

        with self.assertRaises(api.APIError) as raised:
            authenticate_person("sara", "Person@Password1", request=None)

        self.assertEqual(raised.exception.code, "account_locked")

    def test_expired_lock_allows_login_and_clears_failure_count(self):
        authenticate_person = self.function("authenticate_person")
        self.account.failed_login_count = 5
        self.account.locked_until = timezone.now() - timedelta(seconds=1)
        self.account.save(update_fields=["failed_login_count", "locked_until"])

        user = authenticate_person("sara", "Person@Password1", request=None)

        self.assertEqual(user, self.person)
        self.account.refresh_from_db()
        self.assertEqual(self.account.failed_login_count, 0)
        self.assertIsNone(self.account.locked_until)

    def test_role_names_are_normalized_to_contract_roles(self):
        role_codes_for = self.function("role_codes_for")
        user_has_any_role = self.function("user_has_any_role")
        UserAccount.objects.create(
            person=self.person,
            role=self.teacher_role,
            username="teacher-alias",
            password="unused",
        )

        roles = role_codes_for(self.person)

        self.assertEqual(roles, {"student", "professor"})
        self.assertTrue(user_has_any_role(self.person, {"professor", "admin"}))
        self.assertFalse(user_has_any_role(self.person, {"admin"}))

    def test_current_student_only_resolves_records_owned_by_the_person(self):
        current_student = self.function("current_student")
        bachelor_student = self.create_student("S-100", self.bachelor)
        self.create_student("S-101", self.master)

        with self.assertRaises(api.APIError) as ambiguous:
            current_student(self.person)
        self.assertEqual(ambiguous.exception.code, "student_profile_ambiguous")
        self.assertEqual(
            current_student(self.person, "S-100"),
            bachelor_student,
        )
        with self.assertRaises(api.APIError) as not_owned:
            current_student(self.person, "S-999")
        self.assertEqual(not_owned.exception.code, "student_profile_not_found")

    def test_session_configuration_matches_the_idle_timeout_contract(self):
        self.assertEqual(getattr(settings, "SESSION_COOKIE_AGE", None), 900)
        self.assertTrue(getattr(settings, "SESSION_SAVE_EVERY_REQUEST", False))


class AccountAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.person = Person.objects.create_user(
            username="ali",
            password="Person@Password1",
            first_name="علی",
            last_name="آزمون",
            email="ali@example.com",
            national_id="0012345679",
            birth_date=date(2000, 2, 2),
            birth_place="شیراز",
        )
        role = Role.objects.create(role_name="دانشجو")
        UserAccount.objects.create(
            person=cls.person,
            role=role,
            username="ali-account",
            password="not-used-for-authentication",
        )

    def test_login_returns_a_safe_user_summary(self):
        response = self.client.post(
            "/api/accounts/login/",
            data=json.dumps({"username": "ali", "password": "Person@Password1"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "user": {
                    "id": self.person.pk,
                    "username": "ali",
                    "full_name": "علی آزمون",
                    "roles": ["student"],
                }
            },
        )
        self.assertNotIn("national_id", response.json()["user"])

    def test_invalid_login_returns_a_stable_401_error(self):
        response = self.client.post(
            "/api/accounts/login/",
            data=json.dumps({"username": "ali", "password": "wrong"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_credentials",
        )

    def test_current_user_requires_authentication(self):
        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"]["code"], "authentication_required")

    def test_logout_ends_an_authenticated_session(self):
        self.client.force_login(self.person)

        response = self.client.post("/api/accounts/logout/")
        current_user_response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(current_user_response.status_code, 401)

    def protected_view(self):
        try:
            permissions = importlib.import_module("apps.core.accounts.permissions")
        except ModuleNotFoundError:
            self.fail("apps.core.accounts.permissions is not implemented")
        decorator = getattr(permissions, "role_required", None)
        self.assertTrue(callable(decorator), "role_required is not implemented")

        @decorator("student")
        def view(request):
            return JsonResponse({"ok": True})

        return view

    def test_role_required_rejects_anonymous_requests(self):
        request = RequestFactory().get("/api/requests/")
        from django.contrib.auth.models import AnonymousUser

        request.user = AnonymousUser()

        response = self.protected_view()(request)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            json.loads(response.content)["error"]["code"],
            "authentication_required",
        )

    def test_role_required_rejects_users_without_the_required_role(self):
        request = RequestFactory().get("/api/requests/")
        request.user = Person.objects.create_user(
            username="outsider",
            password="Person@Password1",
            first_name="کاربر",
            last_name="دیگر",
            email="outsider@example.com",
            national_id="0098765432",
            birth_date=date(2000, 1, 1),
            birth_place="تهران",
        )

        response = self.protected_view()(request)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            json.loads(response.content)["error"]["code"],
            "permission_denied",
        )

    def test_role_required_allows_users_with_the_required_role(self):
        request = RequestFactory().get("/api/requests/")
        request.user = self.person

        response = self.protected_view()(request)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.content), {"ok": True})

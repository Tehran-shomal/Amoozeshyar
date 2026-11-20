import json
import importlib
from datetime import datetime, timezone as datetime_timezone

from django.apps import apps
from django.conf import settings
from django.test import RequestFactory, SimpleTestCase
from django.urls import get_resolver

from apps.core import api


FEATURES = (
    "enrollment",
    "tuition",
    "grading",
    "requests",
    "scheduling",
    "attendance",
    "classroom",
    "tickets",
    "online_exam",
    "people",
    "student_services",
    "notifications",
    "thesis",
    "accounts",
    "counseling",
    "reports",
    "internship",
    "scholarships",
    "system_settings",
)


class FeatureAppStructureTests(SimpleTestCase):
    def test_expected_feature_apps_are_registered_and_mounted(self):
        installed_labels = {config.label for config in apps.get_app_configs()}
        mounted_prefixes = {
            str(pattern.pattern)
            for pattern in get_resolver().url_patterns
            if hasattr(pattern, "urlconf_name")
        }

        self.assertTrue(set(FEATURES).issubset(installed_labels))
        self.assertTrue(
            {f"api/{feature}/" for feature in FEATURES}.issubset(mounted_prefixes)
        )


class LegacyDateTimeCompatibilityTests(SimpleTestCase):
    def test_timezone_aware_storage_uses_utc_with_an_explicit_legacy_migration_gate(self):
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(settings.TIME_ZONE, "Asia/Tehran")
        self.assertTrue(hasattr(settings, "LEGACY_DATETIME_TIME_ZONE"))

    def test_legacy_datetime_conversion_uses_the_explicit_source_timezone(self):
        migration = importlib.import_module(
            "apps.core.migrations.0004_legacy_datetime_utc"
        )
        loaded_legacy_value = datetime(
            2026, 11, 18, 12, 0, tzinfo=datetime_timezone.utc
        )

        converted = migration._to_utc(loaded_legacy_value, "Asia/Tehran")

        self.assertEqual(
            converted,
            datetime(2026, 11, 18, 8, 30, tzinfo=datetime_timezone.utc),
        )

    def test_status_timestamps_created_by_this_branch_are_not_converted_again(self):
        migration = importlib.import_module(
            "apps.core.migrations.0004_legacy_datetime_utc"
        )
        created_at = datetime(2026, 11, 18, 12, 0, tzinfo=datetime_timezone.utc)
        applied_at = datetime(2026, 11, 18, 12, 0, 1, tzinfo=datetime_timezone.utc)

        self.assertTrue(migration._created_with_migration(created_at, applied_at))
        self.assertFalse(
            migration._created_with_migration(
                created_at,
                datetime(2026, 11, 18, 12, 2, tzinfo=datetime_timezone.utc),
            )
        )

    def test_legacy_datetime_conversion_rejects_ambiguous_or_nonexistent_local_times(self):
        migration = importlib.import_module(
            "apps.core.migrations.0004_legacy_datetime_utc"
        )
        ambiguous = datetime(2026, 11, 1, 1, 30, tzinfo=datetime_timezone.utc)
        nonexistent = datetime(2026, 3, 8, 2, 30, tzinfo=datetime_timezone.utc)

        with self.assertRaises(RuntimeError):
            migration._to_utc(ambiguous, "America/New_York")
        with self.assertRaises(RuntimeError):
            migration._to_utc(nonexistent, "America/New_York")


class JsonApiHelperTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_read_json_accepts_a_json_object(self):
        reader = getattr(api, "read_json", None)
        self.assertTrue(callable(reader), "api.read_json is not implemented")

        request = self.factory.post(
            "/api/example/",
            data='{"offering_id": 12}',
            content_type="application/json",
        )
        self.assertEqual(reader(request), {"offering_id": 12})

    def test_read_json_rejects_invalid_json_and_non_object_json(self):
        reader = getattr(api, "read_json", None)
        api_error = getattr(api, "APIError", None)
        self.assertTrue(callable(reader), "api.read_json is not implemented")
        self.assertTrue(isinstance(api_error, type), "api.APIError is not implemented")

        malformed = self.factory.post(
            "/api/example/", data="{", content_type="application/json"
        )
        scalar = self.factory.post(
            "/api/example/", data="[1]", content_type="application/json"
        )
        for request in (malformed, scalar):
            with self.assertRaises(api_error) as raised:
                reader(request)
            self.assertEqual(raised.exception.status_code, 400)
            self.assertEqual(raised.exception.code, "invalid_json")

    def test_error_response_has_a_stable_json_shape(self):
        responder = getattr(api, "error_response", None)
        self.assertTrue(callable(responder), "api.error_response is not implemented")

        response = responder("invalid_json", "Invalid request", 400)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"error": {"code": "invalid_json", "message": "Invalid request"}},
        )

import json

from django.apps import apps
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

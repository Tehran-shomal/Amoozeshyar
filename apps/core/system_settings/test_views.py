import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.core.models import Constant, Person, SystemSetting


class SystemSettingsAPITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.integer_type = Constant.objects.create(
            category="data_type",
            code="integer",
            label="عدد صحیح",
        )
        cls.decimal_type = Constant.objects.create(
            category="data_type",
            code="decimal",
            label="عدد اعشاری",
        )
        cls.string_type = Constant.objects.create(
            category="data_type",
            code="string",
            label="رشته",
        )
        cls.boolean_type = Constant.objects.create(
            category="data_type",
            code="boolean",
            label="بولی",
        )
        cls.date_type = Constant.objects.create(
            category="data_type",
            code="date",
            label="تاریخ",
        )

        cls.inactive_type = Constant.objects.create(
            category="data_type",
            code="inactive_type",
            label="نوع غیرفعال",
            is_active=False,
        )

        cls.other_category_type = Constant.objects.create(
            category="other_category",
            code="integer",
            label="عدد در دسته دیگر",
        )

        cls.admin = Person.objects.create_user(
            username="system-settings-admin",
            password="TestPassword@123",
            first_name="مدیر",
            last_name="آزمون",
            email="system-settings-admin@example.com",
            national_id="9910000001",
            birth_date=date(1980, 1, 1),
            birth_place="تهران",
            is_staff=True,
            is_superuser=True,
        )

        cls.normal_user = Person.objects.create_user(
            username="system-settings-user",
            password="TestPassword@123",
            first_name="کاربر",
            last_name="آزمون",
            email="system-settings-user@example.com",
            national_id="9910000002",
            birth_date=date(1990, 1, 1),
            birth_place="تهران",
        )

        cls.setting = SystemSetting.objects.create(
            setting_key="test_max_units",
            setting_value="20",
            data_type=cls.integer_type,
            description="تنظیم آزمایشی سقف واحد",
        )

        cls.string_setting = SystemSetting.objects.create(
            setting_key="test_university_name",
            setting_value="دانشگاه آزمایشی",
            data_type=cls.string_type,
            description="نام دانشگاه آزمایشی",
        )

    # --------------------------------------------------
    # Helpers
    # --------------------------------------------------

    def login_as(self, user):
        self.client.force_login(user)

    def list_url(self):
        return reverse("system_settings:setting-list")

    def create_url(self):
        return reverse("system_settings:setting-create")

    def detail_url(self, setting):
        return reverse(
            "system_settings:setting-detail",
            kwargs={"setting_id": setting.pk},
        )

    def update_url(self, setting):
        return reverse(
            "system_settings:setting-update",
            kwargs={"setting_id": setting.pk},
        )

    def json_post(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def json_put(self, url, payload):
        return self.client.put(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def json_patch(self, url, payload):
        return self.client.patch(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    # --------------------------------------------------
    # Authentication and permissions
    # --------------------------------------------------

    def test_anonymous_user_cannot_access_setting_list(self):
        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "authentication_required",
        )

    def test_authenticated_non_admin_cannot_access_setting_list(self):
        self.login_as(self.normal_user)

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error"]["code"],
            "permission_denied",
        )

    def test_non_admin_cannot_create_setting(self):
        self.login_as(self.normal_user)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "unauthorized_setting",
                "setting_value": "10",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(
            SystemSetting.objects.filter(
                setting_key="unauthorized_setting"
            ).exists()
        )

    def test_non_admin_cannot_update_setting(self):
        self.login_as(self.normal_user)

        response = self.json_patch(
            self.update_url(self.setting),
            {"setting_value": "30"},
        )

        self.assertEqual(response.status_code, 403)

        self.setting.refresh_from_db()
        self.assertEqual(self.setting.setting_value, "20")

    # --------------------------------------------------
    # List, search, filter, and pagination
    # --------------------------------------------------

    def test_admin_can_list_system_settings(self):
        self.login_as(self.admin)

        response = self.client.get(self.list_url())

        self.assertEqual(response.status_code, 200)
        self.assertIn("settings", response.json())
        self.assertEqual(response.json()["count"], 2)

    def test_admin_can_search_settings_by_key(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"search": "max_units"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["settings"][0]["setting_key"],
            "test_max_units",
        )

    def test_admin_can_search_settings_by_value(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"search": "دانشگاه آزمایشی"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_admin_can_filter_settings_by_data_type(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"data_type": "integer"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_admin_can_filter_settings_by_data_type_id(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"data_type_id": self.string_type.pk},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

    def test_admin_can_paginate_settings(self):
        self.login_as(self.admin)

        SystemSetting.objects.create(
            setting_key="test_setting_three",
            setting_value="3",
            data_type=self.integer_type,
        )

        response = self.client.get(
            self.list_url(),
            {"page": "1", "page_size": "2"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 3)
        self.assertEqual(response.json()["page"], 1)
        self.assertEqual(response.json()["page_size"], 2)
        self.assertEqual(len(response.json()["settings"]), 2)

    def test_invalid_page_size_returns_400(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"page_size": "101"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_page_size",
        )

    def test_invalid_page_number_returns_400(self):
        self.login_as(self.admin)

        response = self.client.get(
            self.list_url(),
            {"page": "abc"},
        )

        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------
    # Detail
    # --------------------------------------------------

    def test_admin_can_view_setting_detail(self):
        self.login_as(self.admin)

        response = self.client.get(self.detail_url(self.setting))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["setting"]["setting_key"],
            "test_max_units",
        )
        self.assertEqual(
            response.json()["setting"]["setting_value"],
            "20",
        )

    def test_setting_payload_does_not_expose_password(self):
        self.login_as(self.admin)

        response = self.client.get(self.detail_url(self.setting))

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("password", response.json()["setting"])

    def test_nonexistent_setting_detail_returns_404(self):
        self.login_as(self.admin)

        response = self.client.get(
            reverse(
                "system_settings:setting-detail",
                kwargs={"setting_id": 999999},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "setting_not_found",
        )

    # --------------------------------------------------
    # Create
    # --------------------------------------------------

    def test_admin_can_create_integer_setting(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "new_integer_setting",
                "setting_value": "25",
                "data_type_id": self.integer_type.pk,
                "description": "تنظیم عددی جدید",
            },
        )

        self.assertEqual(response.status_code, 201)

        created = SystemSetting.objects.get(
            setting_key="new_integer_setting"
        )

        self.assertEqual(created.setting_value, "25")
        self.assertEqual(created.data_type, self.integer_type)
        self.assertEqual(created.description, "تنظیم عددی جدید")

    def test_create_normalizes_integer_value(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "integer_normalization",
                "setting_value": "+25",
                "data_type_id": self.integer_type.pk,
            },
        )

        self.assertEqual(response.status_code, 201)

        created = SystemSetting.objects.get(
            setting_key="integer_normalization"
        )
        self.assertEqual(created.setting_value, "25")

    def test_admin_can_create_decimal_setting(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "decimal_setting",
                "setting_value": "12.50",
                "data_type_id": self.decimal_type.pk,
            },
        )

        self.assertEqual(response.status_code, 201)

        created = SystemSetting.objects.get(
            setting_key="decimal_setting"
        )
        self.assertEqual(created.setting_value, "12.50")

    def test_admin_can_create_boolean_setting(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "boolean_setting",
                "setting_value": "TRUE",
                "data_type_id": self.boolean_type.pk,
            },
        )

        self.assertEqual(response.status_code, 201)

        created = SystemSetting.objects.get(
            setting_key="boolean_setting"
        )
        self.assertEqual(created.setting_value, "true")

    def test_admin_can_create_date_setting(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "date_setting",
                "setting_value": "2026-11-20",
                "data_type_id": self.date_type.pk,
            },
        )

        self.assertEqual(response.status_code, 201)

    def test_invalid_integer_value_returns_400(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "invalid_integer",
                "setting_value": "not-a-number",
                "data_type_id": self.integer_type.pk,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_setting_value",
        )

    def test_invalid_boolean_value_returns_400(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "invalid_boolean",
                "setting_value": "yes",
                "data_type_id": self.boolean_type.pk,
            },
        )

        self.assertEqual(response.status_code, 400)

    def test_invalid_date_format_returns_400(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "invalid_date",
                "setting_value": "20261120",
                "data_type_id": self.date_type.pk,
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_setting_value",
        )

    def test_inactive_data_type_cannot_be_used(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "inactive_type_setting",
                "setting_value": "10",
                "data_type_id": self.inactive_type.pk,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_wrong_category_data_type_cannot_be_used(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "wrong_category_setting",
                "setting_value": "10",
                "data_type_id": self.other_category_type.pk,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_duplicate_setting_key_returns_409(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "test_max_units",
                "setting_value": "30",
                "data_type_id": self.integer_type.pk,
            },
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(
            response.json()["error"]["code"],
            "duplicate_setting_key",
        )

    def test_missing_required_fields_returns_400(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {"setting_key": "missing_value"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "missing_field",
        )

    def test_unknown_field_returns_400(self):
        self.login_as(self.admin)

        response = self.json_post(
            self.create_url(),
            {
                "setting_key": "unknown_field_setting",
                "setting_value": "10",
                "unexpected_field": "value",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "unknown_fields",
        )

    def test_invalid_json_returns_400(self):
        self.login_as(self.admin)

        response = self.client.post(
            self.create_url(),
            data="{invalid-json",
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_json",
        )

    # --------------------------------------------------
    # Update
    # --------------------------------------------------

    def test_admin_can_patch_setting_value(self):
        self.login_as(self.admin)

        response = self.json_patch(
            self.update_url(self.setting),
            {"setting_value": "30"},
        )

        self.assertEqual(response.status_code, 200)

        self.setting.refresh_from_db()
        self.assertEqual(self.setting.setting_value, "30")

    def test_admin_can_put_setting(self):
        self.login_as(self.admin)

        response = self.json_put(
            self.update_url(self.setting),
            {
                "setting_key": "test_max_units",
                "setting_value": "24",
                "data_type_id": self.integer_type.pk,
                "description": "توضیحات ویرایش‌شده",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.setting.refresh_from_db()
        self.assertEqual(self.setting.setting_value, "24")
        self.assertEqual(
            self.setting.description,
            "توضیحات ویرایش‌شده",
        )

    def test_put_without_required_fields_returns_400(self):
        self.login_as(self.admin)

        response = self.json_put(
            self.update_url(self.setting),
            {"setting_value": "30"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "missing_field",
        )

    def test_patch_can_change_data_type_and_normalize_value(self):
        self.login_as(self.admin)

        setting = SystemSetting.objects.create(
            setting_key="convertible_setting",
            setting_value="+25",
            data_type=None,
        )

        response = self.json_patch(
            self.update_url(setting),
            {"data_type_id": self.integer_type.pk},
        )

        self.assertEqual(response.status_code, 200)

        setting.refresh_from_db()
        self.assertEqual(setting.data_type, self.integer_type)
        self.assertEqual(setting.setting_value, "25")

    def test_patch_rejects_incompatible_new_data_type(self):
        self.login_as(self.admin)

        setting = SystemSetting.objects.create(
            setting_key="incompatible_setting",
            setting_value="not-an-integer",
            data_type=self.string_type,
        )

        response = self.json_patch(
            self.update_url(setting),
            {"data_type_id": self.integer_type.pk},
        )

        self.assertEqual(response.status_code, 400)

        setting.refresh_from_db()
        self.assertEqual(setting.data_type, self.string_type)
        self.assertEqual(setting.setting_value, "not-an-integer")

    def test_patch_can_clear_data_type(self):
        self.login_as(self.admin)

        response = self.json_patch(
            self.update_url(self.setting),
            {"data_type_id": None},
        )

        self.assertEqual(response.status_code, 200)

        self.setting.refresh_from_db()
        self.assertIsNone(self.setting.data_type)

    def test_patch_unknown_field_returns_400(self):
        self.login_as(self.admin)

        response = self.json_patch(
            self.update_url(self.setting),
            {"unknown": "value"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "unknown_fields",
        )

    def test_update_nonexistent_setting_returns_404(self):
        self.login_as(self.admin)

        url = reverse(
            "system_settings:setting-update",
            kwargs={"setting_id": 999999},
        )

        response = self.json_patch(
            url,
            {"setting_value": "30"},
        )

        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------
    # HTTP methods
    # --------------------------------------------------

    def test_system_settings_has_no_delete_endpoint(self):
        self.login_as(self.admin)

        response = self.client.delete(
            self.detail_url(self.setting)
        )

        self.assertEqual(response.status_code, 405)

        self.assertTrue(
            SystemSetting.objects.filter(
                pk=self.setting.pk
            ).exists()
        )

    def test_create_endpoint_rejects_get(self):
        self.login_as(self.admin)

        response = self.client.get(self.create_url())

        self.assertEqual(response.status_code, 405)

    def test_list_endpoint_rejects_post(self):
        self.login_as(self.admin)

        response = self.client.post(self.list_url())

        self.assertEqual(response.status_code, 405)

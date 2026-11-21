from datetime import date
from decimal import Decimal

from django.test import TestCase

from apps.core.models import Constant, SystemSetting
from apps.core.system_settings.reader import (
    get_pagination_settings,
    get_system_setting,
)


class SystemSettingsReaderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.types = {}
        for code, label in (
            ("integer", "عدد صحیح"),
            ("decimal", "عدد اعشاری"),
            ("string", "رشته"),
            ("boolean", "بولی"),
            ("date", "تاریخ"),
            ("unknown", "نوع ناشناخته"),
        ):
            cls.types[code] = Constant.objects.create(
                category="data_type",
                code=code,
                label=label,
            )

    def make_setting(self, key, value, data_type="string"):
        return SystemSetting.objects.create(
            setting_key=key,
            setting_value=value,
            data_type=self.types[data_type],
        )

    def test_reads_integer_setting(self):
        self.make_setting("reader_integer", "42", "integer")
        self.assertEqual(get_system_setting("reader_integer"), 42)

    def test_reads_decimal_setting(self):
        self.make_setting("reader_decimal", "12.50", "decimal")
        self.assertEqual(
            get_system_setting("reader_decimal"),
            Decimal("12.50"),
        )

    def test_reads_string_setting(self):
        self.make_setting("reader_string", "Amoozeshyar", "string")
        self.assertEqual(
            get_system_setting("reader_string"),
            "Amoozeshyar",
        )

    def test_reads_boolean_false_without_treating_it_as_missing(self):
        self.make_setting("reader_boolean", "false", "boolean")
        self.assertIs(get_system_setting("reader_boolean", default=True), False)

    def test_reads_date_setting(self):
        self.make_setting("reader_date", "2026-11-20", "date")
        self.assertEqual(
            get_system_setting("reader_date"),
            date(2026, 11, 20),
        )

    def test_missing_setting_returns_default(self):
        self.assertEqual(
            get_system_setting("does_not_exist", default=17),
            17,
        )

    def test_invalid_setting_value_returns_default(self):
        self.make_setting("reader_invalid", "not-an-integer", "integer")
        self.assertEqual(
            get_system_setting("reader_invalid", default=25),
            25,
        )

    def test_unknown_data_type_returns_default(self):
        self.make_setting("reader_unknown", "anything", "unknown")
        self.assertEqual(
            get_system_setting("reader_unknown", default="fallback"),
            "fallback",
        )

    def test_pagination_uses_stored_values(self):
        self.make_setting("default_page_size", "15", "integer")
        self.make_setting("max_page_size", "60", "integer")
        self.assertEqual(get_pagination_settings(), (15, 60))

    def test_pagination_clamps_default_to_maximum(self):
        self.make_setting("default_page_size", "80", "integer")
        self.make_setting("max_page_size", "30", "integer")
        self.assertEqual(get_pagination_settings(), (30, 30))

    def test_invalid_pagination_values_use_safe_defaults(self):
        self.make_setting("default_page_size", "0", "integer")
        self.make_setting("max_page_size", "invalid", "integer")
        self.assertEqual(get_pagination_settings(), (20, 100))

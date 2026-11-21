import json
from datetime import date

from django.test import TestCase
from django.urls import reverse

from apps.core.models import (
    Communication,
    Constant,
    Person,
    Role,
    SystemSetting,
    UserAccount,
)


class CommunicationAPITests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.sender_person = Person.objects.create_user(
            username="api-communication-sender",
            password="TestPassword@123",
            first_name="فرستنده",
            last_name="آزمایش",
            email="api-sender@example.com",
            national_id="9810000011",
            birth_date=date(1985, 1, 1),
            birth_place="تهران",
        )

        cls.receiver_person = Person.objects.create_user(
            username="api-communication-receiver",
            password="TestPassword@123",
            first_name="گیرنده",
            last_name="آزمایش",
            email="api-receiver@example.com",
            national_id="9810000012",
            birth_date=date(1990, 2, 2),
            birth_place="اصفهان",
        )

        cls.other_person = Person.objects.create_user(
            username="api-communication-other",
            password="TestPassword@123",
            first_name="شخص",
            last_name="دیگر",
            email="api-other@example.com",
            national_id="9810000013",
            birth_date=date(1992, 3, 3),
            birth_place="شیراز",
        )

        cls.sender_role = Role.objects.create(role_name="نقش فرستنده API")
        cls.receiver_role = Role.objects.create(role_name="نقش گیرنده API")
        cls.other_role = Role.objects.create(role_name="نقش دیگر API")

        cls.sender_account = UserAccount.objects.create(
            person=cls.sender_person,
            role=cls.sender_role,
            username="api-sender-account",
            password="not-a-real-login-password",
        )

        cls.receiver_account = UserAccount.objects.create(
            person=cls.receiver_person,
            role=cls.receiver_role,
            username="api-receiver-account",
            password="not-a-real-login-password",
        )

        cls.other_account = UserAccount.objects.create(
            person=cls.other_person,
            role=cls.other_role,
            username="api-other-account",
            password="not-a-real-login-password",
        )

        cls.official_type = Constant.objects.create(
            category="communication_type",
            code="official",
            label="رسمی",
        )

        cls.unread_status = Constant.objects.create(
            category="communication_status",
            code="unread",
            label="خوانده نشده",
        )

        cls.read_status = Constant.objects.create(
            category="communication_status",
            code="read",
            label="خوانده شده",
        )

    def setUp(self):
        self.client.force_login(self.sender_person)

    def create_communication(self, **kwargs):
        defaults = {
            "sender": self.sender_account,
            "receiver": self.receiver_account,
            "subject": "موضوع آزمایشی",
            "message_body": "متن پیام آزمایشی",
            "status": self.unread_status,
        }
        defaults.update(kwargs)
        return Communication.objects.create(**defaults)

    def set_pagination_setting(self, key, value):
        integer_type, _ = Constant.objects.get_or_create(
            category="data_type",
            code="integer",
            defaults={"label": "عدد صحیح"},
        )

        SystemSetting.objects.update_or_create(
            setting_key=key,
            defaults={
                "setting_value": str(value),
                "data_type": integer_type,
            },
        )

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    # ------------------------------------------
    # Authentication
    # ------------------------------------------

    def test_anonymous_user_cannot_access_inbox(self):
        self.client.logout()

        response = self.client.get(reverse("communication:inbox"))

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json()["error"]["code"],
            "authentication_required",
        )

    def test_anonymous_user_cannot_send_message(self):
        self.client.logout()

        response = self.post_json(
            reverse("communication:send"),
            {
                "receiver_account_id": self.receiver_account.pk,
                "subject": "موضوع",
                "message_body": "متن پیام",
            },
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Communication.objects.count(), 0)

    # ------------------------------------------
    # Sending messages
    # ------------------------------------------

    def test_authenticated_user_can_send_message(self):
        response = self.post_json(
            reverse("communication:send"),
            {
                "receiver_account_id": self.receiver_account.pk,
                "subject": "  اطلاعیه جدید  ",
                "message_body": "  متن اطلاعیه  ",
                "communication_type_code": "official",
            },
        )

        self.assertEqual(response.status_code, 201)

        data = response.json()["communication"]

        self.assertEqual(data["subject"], "اطلاعیه جدید")
        self.assertEqual(data["message_body"], "متن اطلاعیه")
        self.assertEqual(data["sender"]["id"], self.sender_account.pk)
        self.assertEqual(data["receiver"]["id"], self.receiver_account.pk)
        self.assertEqual(data["communication_type"]["code"], "official")
        self.assertFalse(data["is_read"])
        self.assertNotIn("password", json.dumps(data))

        self.assertEqual(Communication.objects.count(), 1)

    def test_user_cannot_send_message_using_another_person_account(self):
        response = self.post_json(
            reverse("communication:send"),
            {
                "sender_account_id": self.other_account.pk,
                "receiver_account_id": self.receiver_account.pk,
                "subject": "موضوع",
                "message_body": "متن پیام",
            },
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(
            response.json()["error"]["code"],
            "sender_account_not_available",
        )
        self.assertEqual(Communication.objects.count(), 0)

    def test_sender_account_is_required_when_user_has_multiple_accounts(self):
        second_role = Role.objects.create(
            role_name="نقش دوم فرستنده API",
        )
        UserAccount.objects.create(
            person=self.sender_person,
            role=second_role,
            username="api-sender-second-account",
            password="not-a-real-login-password",
        )

        response = self.post_json(
            reverse("communication:send"),
            {
                "receiver_account_id": self.receiver_account.pk,
                "subject": "موضوع",
                "message_body": "متن پیام",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "sender_account_required",
        )

    def test_send_rejects_missing_subject(self):
        response = self.post_json(
            reverse("communication:send"),
            {
                "receiver_account_id": self.receiver_account.pk,
                "message_body": "متن پیام",
            },
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_subject",
        )

    # ------------------------------------------
    # Inbox and outbox
    # ------------------------------------------

    def test_inbox_only_returns_messages_received_by_user(self):
        received = self.create_communication()
        self.create_communication(receiver=self.other_account)

        self.client.force_login(self.receiver_person)

        response = self.client.get(reverse("communication:inbox"))

        self.assertEqual(response.status_code, 200)

        results = response.json()["inbox"]["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], received.pk)

    def test_outbox_only_returns_messages_sent_by_user(self):
        sent = self.create_communication()
        self.create_communication(sender=self.other_account)

        response = self.client.get(reverse("communication:outbox"))

        self.assertEqual(response.status_code, 200)

        results = response.json()["outbox"]["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], sent.pk)

    # ------------------------------------------
    # Message detail and access control
    # ------------------------------------------

    def test_sender_can_view_message_detail(self):
        message = self.create_communication()

        response = self.client.get(
            reverse(
                "communication:detail",
                kwargs={"communication_id": message.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json()["communication"]["id"],
            message.pk,
        )

    def test_unrelated_user_cannot_view_message_detail(self):
        message = self.create_communication()
        self.client.force_login(self.other_person)

        response = self.client.get(
            reverse(
                "communication:detail",
                kwargs={"communication_id": message.pk},
            )
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json()["error"]["code"],
            "communication_not_found",
        )

    # ------------------------------------------
    # Read and unread actions
    # ------------------------------------------

    def test_receiver_can_mark_message_as_read(self):
        message = self.create_communication()
        self.client.force_login(self.receiver_person)

        response = self.client.post(
            reverse(
                "communication:mark_read",
                kwargs={"communication_id": message.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        message.refresh_from_db()

        self.assertTrue(message.is_read)
        self.assertIsNotNone(message.read_at)
        self.assertEqual(message.status, self.read_status)

    def test_sender_cannot_mark_own_message_as_read(self):
        message = self.create_communication()

        response = self.client.post(
            reverse(
                "communication:mark_read",
                kwargs={"communication_id": message.pk},
            )
        )

        self.assertEqual(response.status_code, 403)
        self.assertFalse(message.is_read)

    def test_receiver_can_mark_message_as_unread(self):
        message = self.create_communication(
            status=self.read_status,
            is_read=True,
        )
        self.client.force_login(self.receiver_person)

        response = self.client.post(
            reverse(
                "communication:mark_unread",
                kwargs={"communication_id": message.pk},
            )
        )

        self.assertEqual(response.status_code, 200)

        message.refresh_from_db()

        self.assertFalse(message.is_read)
        self.assertIsNone(message.read_at)
        self.assertEqual(message.status, self.unread_status)

    # ------------------------------------------
    # Search and pagination
    # ------------------------------------------

    def test_inbox_search_filters_messages(self):
        matching = self.create_communication(
            subject="اطلاعیه امتحان",
        )
        self.create_communication(
            subject="جلسه آموزشی",
        )

        self.client.force_login(self.receiver_person)

        response = self.client.get(
            reverse("communication:inbox"),
            {"search": "امتحان"},
        )

        self.assertEqual(response.status_code, 200)

        results = response.json()["inbox"]["results"]

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], matching.pk)

    def test_inbox_pagination_returns_requested_page(self):
        for index in range(5):
            self.create_communication(
                subject=f"پیام شماره {index}",
            )

        self.client.force_login(self.receiver_person)

        response = self.client.get(
            reverse("communication:inbox"),
            {"page": 2, "page_size": 2},
        )

        self.assertEqual(response.status_code, 200)

        data = response.json()["inbox"]

        self.assertEqual(data["count"], 5)
        self.assertEqual(data["page"], 2)
        self.assertEqual(data["page_size"], 2)
        self.assertEqual(data["total_pages"], 3)
        self.assertEqual(len(data["results"]), 2)

    def test_inbox_default_page_size_comes_from_system_settings(self):
        for index in range(3):
            self.create_communication(subject=f"پیام ورودی {index}")

        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.client.force_login(self.receiver_person)

        response = self.client.get(reverse("communication:inbox"))

        self.assertEqual(response.status_code, 200)

        data = response.json()["inbox"]
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["page_size"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["total_pages"], 3)

    def test_outbox_default_page_size_comes_from_system_settings(self):
        for index in range(3):
            self.create_communication(subject=f"پیام خروجی {index}")

        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)
        self.client.force_login(self.sender_person)

        response = self.client.get(reverse("communication:outbox"))

        self.assertEqual(response.status_code, 200)

        data = response.json()["outbox"]
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["page_size"], 1)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["total_pages"], 3)

    def test_page_size_above_system_maximum_is_rejected(self):
        self.set_pagination_setting("default_page_size", 1)
        self.set_pagination_setting("max_page_size", 2)

        response = self.client.get(
            reverse("communication:inbox"),
            {"page_size": 3},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_page_size",
        )

    def test_invalid_page_size_is_rejected(self):
        response = self.client.get(
            reverse("communication:inbox"),
            {"page_size": 101},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.json()["error"]["code"],
            "invalid_page_size",
        )

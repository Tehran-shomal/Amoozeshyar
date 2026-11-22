from datetime import date

from django.test import TestCase
from django.utils import timezone

from apps.core.api import APIError
from apps.core.models import Communication, Constant, Person, Role, UserAccount
from apps.core.communication.services import (
    active_accounts_for_person,
    communications_for_inbox,
    communications_for_outbox,
    get_communication_for_person,
    mark_communication_read,
    mark_communication_unread,
    resolve_receiver_account,
    resolve_sender_account,
    send_communication,
)


class CommunicationServiceTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.sender_person = Person.objects.create_user(
            username="communication-sender",
            password="TestPassword@123",
            first_name="فرستنده",
            last_name="آزمون",
            email="communication-sender@example.com",
            national_id="9810000001",
            birth_date=date(1985, 1, 1),
            birth_place="تهران",
        )

        cls.receiver_person = Person.objects.create_user(
            username="communication-receiver",
            password="TestPassword@123",
            first_name="گیرنده",
            last_name="آزمون",
            email="communication-receiver@example.com",
            national_id="9810000002",
            birth_date=date(1990, 2, 2),
            birth_place="اصفهان",
        )

        cls.other_person = Person.objects.create_user(
            username="communication-other",
            password="TestPassword@123",
            first_name="شخص",
            last_name="دیگر",
            email="communication-other@example.com",
            national_id="9810000003",
            birth_date=date(1992, 3, 3),
            birth_place="شیراز",
        )

        cls.sender_role = Role.objects.create(role_name="نقش فرستنده")
        cls.receiver_role = Role.objects.create(role_name="نقش گیرنده")
        cls.other_role = Role.objects.create(role_name="نقش دیگر")

        cls.sender_account = UserAccount.objects.create(
            person=cls.sender_person,
            role=cls.sender_role,
            username="communication-sender-account",
            password="not-a-real-login-password",
        )

        cls.receiver_account = UserAccount.objects.create(
            person=cls.receiver_person,
            role=cls.receiver_role,
            username="communication-receiver-account",
            password="not-a-real-login-password",
        )

        cls.other_account = UserAccount.objects.create(
            person=cls.other_person,
            role=cls.other_role,
            username="communication-other-account",
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

        cls.replied_status = Constant.objects.create(
            category="communication_status",
            code="replied",
            label="پاسخ داده شده",
        )

    def create_communication(self, **kwargs):
        defaults = {
            "sender": self.sender_account,
            "receiver": self.receiver_account,
            "subject": "موضوع آزمون",
            "message_body": "متن پیام آزمایشی",
            "status": self.unread_status,
        }
        defaults.update(kwargs)
        return Communication.objects.create(**defaults)

    # ------------------------------------------
    # Account resolution and ownership
    # ------------------------------------------

    def test_active_accounts_only_include_active_accounts_and_roles(self):
        inactive_account = UserAccount.objects.create(
            person=self.sender_person,
            role=self.sender_role,
            username="communication-inactive-account",
            password="not-a-real-login-password",
            is_active=False,
        )

        inactive_role = Role.objects.create(
            role_name="نقش غیرفعال",
            is_active=False,
        )
        inactive_role_account = UserAccount.objects.create(
            person=self.sender_person,
            role=inactive_role,
            username="communication-inactive-role-account",
            password="not-a-real-login-password",
        )

        accounts = active_accounts_for_person(self.sender_person)

        self.assertIn(self.sender_account, accounts)
        self.assertNotIn(inactive_account, accounts)
        self.assertNotIn(inactive_role_account, accounts)

    def test_sender_account_is_resolved_for_its_owner(self):
        account = resolve_sender_account(
            self.sender_person,
            self.sender_account.pk,
        )
        self.assertEqual(account, self.sender_account)

    def test_sender_cannot_select_another_person_account(self):
        with self.assertRaises(APIError) as raised:
            resolve_sender_account(
                self.sender_person,
                self.other_account.pk,
            )

        self.assertEqual(raised.exception.status_code, 403)
        self.assertEqual(
            raised.exception.code,
            "sender_account_not_available",
        )

    def test_sender_account_is_required_when_multiple_active_accounts_exist(self):
        second_role = Role.objects.create(role_name="نقش دوم فرستنده")
        UserAccount.objects.create(
            person=self.sender_person,
            role=second_role,
            username="communication-sender-second-account",
            password="not-a-real-login-password",
        )

        with self.assertRaises(APIError) as raised:
            resolve_sender_account(self.sender_person)

        self.assertEqual(
            raised.exception.code,
            "sender_account_required",
        )

    def test_sender_account_id_must_be_an_integer(self):
        with self.assertRaises(APIError) as raised:
            resolve_sender_account(self.sender_person, True)

        self.assertEqual(
            raised.exception.code,
            "invalid_sender_account",
        )

    def test_receiver_must_be_active_and_have_an_active_role(self):
        inactive_account = UserAccount.objects.create(
            person=self.other_person,
            role=self.other_role,
            username="communication-inactive-receiver",
            password="not-a-real-login-password",
            is_active=False,
        )

        with self.assertRaises(APIError) as raised:
            resolve_receiver_account(inactive_account.pk)

        self.assertEqual(raised.exception.status_code, 404)

        self.other_role.is_active = False
        self.other_role.save(update_fields=["is_active"])

        with self.assertRaises(APIError):
            resolve_receiver_account(self.other_account.pk)

    # ------------------------------------------
    # Sending communications
    # ------------------------------------------

    def test_send_communication_creates_message_with_expected_fields(self):
        communication = send_communication(
            person=self.sender_person,
            receiver_account_id=self.receiver_account.pk,
            sender_account_id=self.sender_account.pk,
            subject="  اطلاعیه آزمون  ",
            message_body="  متن اطلاعیه  ",
            communication_type_code="official",
        )

        self.assertEqual(communication.sender, self.sender_account)
        self.assertEqual(communication.receiver, self.receiver_account)
        self.assertEqual(communication.subject, "اطلاعیه آزمون")
        self.assertEqual(communication.message_body, "متن اطلاعیه")
        self.assertEqual(communication.communication_type, self.official_type)
        self.assertEqual(communication.status, self.unread_status)
        self.assertFalse(communication.is_read)
        self.assertIsNone(communication.read_at)
        self.assertIsNotNone(communication.sent_at)

    def test_send_communication_rejects_empty_subject(self):
        with self.assertRaises(APIError) as raised:
            send_communication(
                person=self.sender_person,
                receiver_account_id=self.receiver_account.pk,
                subject="   ",
                message_body="متن پیام",
            )

        self.assertEqual(raised.exception.code, "invalid_subject")
        self.assertEqual(Communication.objects.count(), 0)

    def test_send_communication_rejects_empty_message_body(self):
        with self.assertRaises(APIError) as raised:
            send_communication(
                person=self.sender_person,
                receiver_account_id=self.receiver_account.pk,
                subject="موضوع",
                message_body="   ",
            )

        self.assertEqual(raised.exception.code, "invalid_message_body")
        self.assertEqual(Communication.objects.count(), 0)

    def test_send_communication_rejects_invalid_communication_type(self):
        with self.assertRaises(APIError) as raised:
            send_communication(
                person=self.sender_person,
                receiver_account_id=self.receiver_account.pk,
                subject="موضوع",
                message_body="متن پیام",
                communication_type_code="not-a-valid-type",
            )

        self.assertEqual(
            raised.exception.code,
            "invalid_communication_type",
        )
        self.assertEqual(Communication.objects.count(), 0)

    # ------------------------------------------
    # Inbox, outbox and detail visibility
    # ------------------------------------------

    def test_inbox_returns_messages_received_by_person_accounts(self):
        message = self.create_communication()

        second_role = Role.objects.create(
            role_name="نقش دوم گیرنده",
        )
        second_receiver_account = UserAccount.objects.create(
            person=self.receiver_person,
            role=second_role,
            username="communication-receiver-second-account",
            password="not-a-real-login-password",
        )

        second_message = self.create_communication(
            receiver=second_receiver_account,
            subject="پیام حساب دوم",
        )

        self.create_communication(receiver=self.other_account)

        inbox = communications_for_inbox(self.receiver_person)

        self.assertEqual(
            set(inbox.values_list("communication_id", flat=True)),
            {message.pk, second_message.pk},
        )

    def test_outbox_returns_messages_sent_by_person_accounts(self):
        message = self.create_communication()

        second_role = Role.objects.create(
            role_name="نقش دوم فرستنده",
        )
        second_sender_account = UserAccount.objects.create(
            person=self.sender_person,
            role=second_role,
            username="communication-sender-second-outbox",
            password="not-a-real-login-password",
        )

        second_message = self.create_communication(
            sender=second_sender_account,
            subject="پیام حساب دوم",
        )

        self.create_communication(sender=self.other_account)

        outbox = communications_for_outbox(self.sender_person)

        self.assertEqual(
            set(outbox.values_list("communication_id", flat=True)),
            {message.pk, second_message.pk},
        )

    def test_sender_and_receiver_can_view_message_detail(self):
        message = self.create_communication()

        self.assertEqual(
            get_communication_for_person(
                self.sender_person,
                message.pk,
            ),
            message,
        )

        self.assertEqual(
            get_communication_for_person(
                self.receiver_person,
                message.pk,
            ),
            message,
        )

    def test_unrelated_person_cannot_view_message_detail(self):
        message = self.create_communication()

        with self.assertRaises(APIError) as raised:
            get_communication_for_person(
                self.other_person,
                message.pk,
            )

        self.assertEqual(raised.exception.status_code, 404)
        self.assertEqual(
            raised.exception.code,
            "communication_not_found",
        )

    def test_invalid_communication_id_is_rejected(self):
        for invalid_id in (True, "1", 1.5, None):
            with self.subTest(invalid_id=invalid_id):
                with self.assertRaises(APIError) as raised:
                    get_communication_for_person(
                        self.sender_person,
                        invalid_id,
                    )

                self.assertEqual(
                    raised.exception.code,
                    "invalid_communication_id",
                )

    # ------------------------------------------
    # Read and unread state
    # ------------------------------------------

    def test_receiver_can_mark_message_as_read(self):
        message = self.create_communication()

        result = mark_communication_read(
            self.receiver_person,
            message.pk,
        )

        result.refresh_from_db()

        self.assertTrue(result.is_read)
        self.assertIsNotNone(result.read_at)
        self.assertTrue(timezone.is_aware(result.read_at))
        self.assertEqual(result.status, self.read_status)

    def test_marking_replied_message_as_read_preserves_replied_status(self):
        message = self.create_communication(
            status=self.replied_status,
        )

        result = mark_communication_read(
            self.receiver_person,
            message.pk,
        )

        self.assertTrue(result.is_read)
        self.assertEqual(result.status, self.replied_status)

    def test_receiver_can_mark_message_as_unread(self):
        message = self.create_communication(
            status=self.read_status,
            is_read=True,
            read_at=timezone.now(),
        )

        result = mark_communication_unread(
            self.receiver_person,
            message.pk,
        )

        self.assertFalse(result.is_read)
        self.assertIsNone(result.read_at)
        self.assertEqual(result.status, self.unread_status)

    def test_marking_replied_message_as_unread_preserves_replied_status(self):
        message = self.create_communication(
            status=self.replied_status,
            is_read=True,
            read_at=timezone.now(),
        )

        result = mark_communication_unread(
            self.receiver_person,
            message.pk,
        )

        self.assertFalse(result.is_read)
        self.assertIsNone(result.read_at)
        self.assertEqual(result.status, self.replied_status)

    def test_sender_cannot_change_read_state(self):
        message = self.create_communication()

        with self.assertRaises(APIError) as raised:
            mark_communication_read(
                self.sender_person,
                message.pk,
            )

        self.assertEqual(raised.exception.status_code, 403)

        with self.assertRaises(APIError) as raised:
            mark_communication_unread(
                self.sender_person,
                message.pk,
            )

        self.assertEqual(raised.exception.status_code, 403)

    def test_unrelated_person_cannot_change_read_state(self):
        message = self.create_communication()

        with self.assertRaises(APIError) as raised:
            mark_communication_read(
                self.other_person,
                message.pk,
            )

        self.assertEqual(raised.exception.status_code, 404)

    def test_marking_already_read_message_does_not_change_read_timestamp(self):
        original_read_at = timezone.now()
        message = self.create_communication(
            status=self.read_status,
            is_read=True,
            read_at=original_read_at,
        )

        result = mark_communication_read(
            self.receiver_person,
            message.pk,
        )

        self.assertEqual(result.read_at, original_read_at)

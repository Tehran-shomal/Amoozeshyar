from django.test import SimpleTestCase
from django.urls import reverse


class PortalTemplateContractTests(SimpleTestCase):
    """Pin the browser hooks used by the existing session API (SSOT §4)."""

    def test_login_preview_exposes_named_credentials_and_a_live_status(self):
        response = self.client.get(reverse("core:login-preview"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password"')
        self.assertContains(response, 'type="submit"')
        self.assertContains(response, 'data-login-status')
        self.assertContains(response, 'aria-live="polite"')
        self.assertContains(response, "نام کاربری")
        self.assertContains(response, "گذرواژه")

    def test_portal_sidebar_exposes_a_logout_action_and_status(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_course_selector_requires_a_signed_in_student(self):
        response = self.client.get(reverse("core:section", kwargs={"slug": "selected-courses"}))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

    def test_drop_page_requires_a_signed_in_student(self):
        response = self.client.get(reverse("core:section", kwargs={"slug": "add-drop"}))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login/", response.url)

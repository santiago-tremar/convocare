from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core import mail
from django.test import override_settings
from django.urls import reverse


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminEmailTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser",
            email="testuser@example.com",
            password="testpass123",
        )

    def test_poster_request_sends_admin_email(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("poster_request"),
            {
                "poster_type": "GROUP",
                "poster_name": "Test Group",
                "address": "123 Test Street",
                "preferred_media": "email",
                "contact": "contact@example.com",
            },
        )

        self.assertRedirects(response, reverse("poster_request_complete"))
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["john@appleseed.com"])
        self.assertIn("Solicitud para registrar un nuevo posteador", message.subject)
        self.assertIn("testuser", message.body)
        self.assertIn("Test Group", message.body)
        self.assertIn("contact@example.com", message.body)

    def test_invalid_poster_request_does_not_send_email(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse("poster_request"),
            {
                "poster_type": "INVALID",
                "poster_name": "",
                "address": "123 Test Street",
                "preferred_media": "email",
                "contact": "contact@example.com",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox, [])

    def test_contact_admin_sends_admin_email(self):
        response = self.client.post(
            reverse("contact_admin"),
            {
                "username": "Guest User",
                "email": "guest@example.com",
                "message": "Please help me.",
            },
        )

        self.assertRedirects(response, reverse("contact_admin_complete"))
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertEqual(message.to, ["john@appleseed.com"])
        self.assertIn("Mensaje de Guest User", message.subject)
        self.assertIn("guest@example.com", message.body)
        self.assertIn("Please help me.", message.body)

    def test_invalid_contact_admin_form_does_not_send_email(self):
        response = self.client.post(
            reverse("contact_admin"),
            {
                "username": "Guest User",
                "email": "not-an-email",
                "message": "Please help me.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(mail.outbox, [])

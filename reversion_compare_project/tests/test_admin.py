from bx_django_utils.test_utils.html_assertion import HtmlAssertionMixin
from django.apps import apps
from django.contrib.auth.models import User
from django.test import TestCase
from model_bakery import baker
from reversion import get_registered_models


class AdminAnonymousTests(HtmlAssertionMixin, TestCase):
    """
    Anonymous will be redirected to the login page.
    """

    def test_login_en(self):
        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assertRedirects(response, expected_url="/en/admin/login/?next=/en/admin/")

    def test_login_de(self):
        response = self.client.get("/de/admin/", HTTP_ACCEPT_LANGUAGE="de")
        self.assertRedirects(response, expected_url="/de/admin/login/?next=/de/admin/")


class AdminLoggedinTests(HtmlAssertionMixin, TestCase):
    """
    Some basics test with the django admin
    """

    @classmethod
    def setUpTestData(cls):
        cls.superuser = baker.make(User, username='superuser', is_staff=True, is_active=True, is_superuser=True)
        cls.staffuser = baker.make(User, username='staff_test_user', is_staff=True, is_active=True, is_superuser=False)

    def test_admin_login(self):
        response = self.client.get('/admin/')
        self.assertRedirects(response, expected_url='/en/admin/', fetch_redirect_response=False)
        response = self.client.get('/en/admin/')
        self.assertRedirects(response, expected_url='/en/admin/login/?next=/en/admin/', fetch_redirect_response=False)

        self.client.force_login(self.staffuser)
        response = self.client.get('/en/admin/')
        self.assertEqual(response.status_code, 200, response)
        self.assert_html_parts(response, parts=('<strong>staff_test_user</strong>',))

    def test_model_registering(self):
        test_app_config = apps.get_app_config(app_label='reversion_compare_project')
        models = test_app_config.get_models(include_auto_created=False, include_swapped=False)
        default_registered = len(list(get_registered_models()))
        self.assertEqual(default_registered, len(tuple(models)))

    def test_staff_admin_index(self):
        self.client.force_login(self.staffuser)

        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assert_html_parts(
            response,
            parts=(
                "<title>Reversion Compare Test | Site administration</title>",
                "<h1>Site administration</h1>",
                "<strong>staff_test_user</strong>",
                "<p>You don’t have permission to view or edit anything.</p>",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")

    def test_superuser_admin_index(self):
        self.client.force_login(self.superuser)
        response = self.client.get("/en/admin/", HTTP_ACCEPT_LANGUAGE="en")
        self.assert_html_parts(
            response,
            parts=(
                "reversion_compare",
                "<strong>superuser</strong>",
                "Site administration",
                "/admin/auth/group/add/",
                "/admin/auth/user/add/",
            ),
        )
        self.assertTemplateUsed(response, template_name="admin/index.html")

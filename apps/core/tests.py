from django.templatetags.static import static
from django.template.loader import render_to_string
from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse
from allauth.socialaccount.models import SocialApp


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)
class HomeViewTests(TestCase):
    def setUp(self):
        self.google_app = SocialApp.objects.create(
            provider="google",
            name="Google OAuth",
            client_id="test-google-client-id",
            secret="test-google-secret",
        )
        self.google_app.sites.add(Site.objects.get_current())

    @override_settings(STATIC_URL="/assets/")
    def test_base_template_renders_shared_resources_and_navigation_once(self):
        request = RequestFactory().get("/")

        response = render_to_string("core/base.html", request=request)

        self.assertEqual(
            response.count('src="https://cdn.tailwindcss.com"'),
            1,
        )
        self.assertEqual(
            response.count(f'href="{static("myproject1/css/site.css")}?v=pink-theme-v3"'),
            1,
        )
        self.assertEqual(response.count('data-site-navbar'), 1)
        self.assertIn(f'href="{reverse("core:home")}"', response)
        self.assertIn(f'href="{reverse("core:home")}#how"', response)
        self.assertIn(f'href="{reverse("core:home")}#categories"', response)

    @override_settings(STATIC_URL="/assets/")
    def test_home_uses_external_stylesheet_and_keeps_key_controls(self):
        response = self.client.get(reverse("core:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'href="{static("myproject1/css/home.css")}"',
        )
        self.assertNotContains(response, "<style>")
        self.assertContains(response, reverse("chillme:event-list"))
        self.assertContains(response, 'id="homepage-search"')

    @override_settings(
        STORAGES={
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        },
    )
    def test_activity_and_login_pages_use_the_shared_shell(self):
        for url, expected_content in (
            (reverse("chillme:event-list"), "揪命啊｜揪團活動"),
            (reverse("account_login"), "歡迎回到揪命啊！"),
        ):
            with self.subTest(url=url):
                response = self.client.get(url)

                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected_content)
                self.assertEqual(response.content.count(b"data-site-navbar"), 1)
                self.assertContains(response, f'href="{reverse("core:home")}#how"')

    def test_login_page_offers_configured_google_login_without_removing_password_login(
        self,
    ):
        response = self.client.get(reverse("account_login"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "使用 Google 登入")
        self.assertContains(response, f'href="{reverse("google_login")}"')
        self.assertContains(response, f'action="{reverse("account_login")}"')
        self.assertContains(response, f'href="{reverse("account_signup")}"')

    @override_settings(
        STORAGES={
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        },
    )
    def test_navigation_actions_follow_authentication_state(self):
        anonymous_response = self.client.get(reverse("core:home"))

        self.assertContains(anonymous_response, reverse("account_login"))
        self.assertContains(anonymous_response, reverse("account_signup"))
        self.assertNotContains(anonymous_response, 'action="/accounts/logout/"')

        user = get_user_model().objects.create_user(
            username="navbar-user",
            password="safe-password",
        )
        self.client.force_login(user)

        authenticated_response = self.client.get(reverse("core:home"))

        self.assertContains(authenticated_response, reverse("chillme:event-create"))
        self.assertContains(
            authenticated_response,
            f'action="{reverse("account_logout")}"',
        )
        self.assertContains(authenticated_response, 'method="post"')
        self.assertContains(authenticated_response, 'csrfmiddlewaretoken')

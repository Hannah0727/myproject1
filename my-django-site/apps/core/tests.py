from django.templatetags.static import static
from django.test import TestCase, override_settings
from django.urls import reverse


class HomeViewTests(TestCase):
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

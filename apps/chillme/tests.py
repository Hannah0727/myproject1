from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import Event


@override_settings(
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)
class EventListDataViewTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(
            username="organizer",
            password="test-password",
        )
        for number in range(21):
            Event.objects.create(
                name=f"羽球活動 {number}",
                code=f"B{number:02d}",
                owner=self.owner,
            )
        Event.objects.create(
            name="桌遊同好會",
            code="BOARD",
            owner=self.owner,
        )

    def test_returns_first_page_with_pagination_metadata(self):
        response = self.client.get(reverse("chillme:event-list-data"))

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(len(payload["items"]), 20)
        self.assertEqual(payload["pagination"], {
            "page": 1,
            "total_pages": 2,
            "total_count": 22,
            "has_previous": False,
            "has_next": True,
        })
        self.assertEqual(payload["query"], "")
        self.assertEqual(payload["items"][0]["owner_name"], "organizer")

    def test_filters_and_preserves_query_on_requested_page(self):
        response = self.client.get(
            reverse("chillme:event-list-data"),
            {"q": " 羽球 ", "page": 2},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["query"], "羽球")
        self.assertEqual(payload["pagination"]["page"], 2)
        self.assertEqual(payload["pagination"]["total_count"], 21)
        self.assertEqual(len(payload["items"]), 1)
        self.assertEqual(payload["items"][0]["name"], "羽球活動 0")

    def test_normalizes_invalid_and_out_of_range_page_numbers(self):
        data_url = reverse("chillme:event-list-data")

        invalid_response = self.client.get(data_url, {"page": "zero"})
        out_of_range_response = self.client.get(data_url, {"page": 99})

        self.assertEqual(invalid_response.json()["pagination"]["page"], 1)
        self.assertEqual(out_of_range_response.json()["pagination"]["page"], 2)

    def test_returns_an_empty_page_for_a_query_without_matches(self):
        response = self.client.get(
            reverse("chillme:event-list-data"),
            {"q": "不存在"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["items"], [])
        self.assertEqual(response.json()["pagination"], {
            "page": 1,
            "total_pages": 1,
            "total_count": 0,
            "has_previous": False,
            "has_next": False,
        })

    def test_event_list_shell_exposes_the_data_endpoint(self):
        response = self.client.get(reverse("chillme:event-list"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            reverse("chillme:event-list-data"),
        )
        self.assertContains(response, "event-list.js")

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import transaction
from django.test import TestCase, override_settings
from django.urls import reverse
from unittest.mock import patch

from .models import Event, Registration
from .views import EVENT_LIST_CACHE_VERSION_KEY


@override_settings(
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "event-list-tests",
        },
    },
    STORAGES={
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    },
)
class EventListDataViewTests(TestCase):
    def setUp(self):
        cache.clear()
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

    def test_reuses_a_cached_response_for_the_same_normalized_request(self):
        data_url = reverse("chillme:event-list-data")

        with patch(
            "apps.chillme.views.Event.objects.select_related",
            wraps=Event.objects.select_related,
        ) as select_related:
            self.client.get(data_url, {"q": " 羽球 ", "page": 1})
            self.client.get(data_url, {"q": "羽球", "page": 1})

        self.assertEqual(select_related.call_count, 1)

    def test_returns_data_when_the_cache_read_fails(self):
        data_url = reverse("chillme:event-list-data")

        with patch("apps.chillme.views.cache", create=True) as mocked_cache:
            mocked_cache.get.side_effect = ConnectionError
            response = self.client.get(data_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["items"]), 20)
        mocked_cache.get.assert_called_once()

    def test_creating_an_event_advances_the_cache_version_after_commit(self):
        self.client.get(reverse("chillme:event-list-data"))
        initial_version = cache.get(EVENT_LIST_CACHE_VERSION_KEY)

        with self.captureOnCommitCallbacks(execute=True):
            Event.objects.create(
                name="快取後新增的活動",
                code="NEW-CACHE",
                owner=self.owner,
            )

        self.assertEqual(cache.get(EVENT_LIST_CACHE_VERSION_KEY), initial_version + 1)

    def test_rolled_back_event_creation_keeps_the_cache_version(self):
        self.client.get(reverse("chillme:event-list-data"))
        initial_version = cache.get(EVENT_LIST_CACHE_VERSION_KEY)

        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                Event.objects.create(
                    name="取消建立的活動",
                    code="ROLLED-BACK",
                    owner=self.owner,
                )
                raise RuntimeError("rollback")

        self.assertEqual(cache.get(EVENT_LIST_CACHE_VERSION_KEY), initial_version)

    def test_event_creation_invalidates_cached_search_and_page_variants(self):
        data_url = reverse("chillme:event-list-data")
        self.client.get(data_url, {"page": 1})
        self.client.get(data_url, {"q": "新活動", "page": 1})
        self.client.get(data_url, {"page": 2})

        with self.captureOnCommitCallbacks(execute=True):
            Event.objects.create(
                name="新活動快取失效測試",
                code="INVALIDATE",
                owner=self.owner,
            )

        first_page = self.client.get(data_url, {"page": 1}).json()
        searched_page = self.client.get(data_url, {"q": "新活動", "page": 1}).json()
        second_page = self.client.get(data_url, {"page": 2}).json()

        self.assertEqual(first_page["pagination"]["total_count"], 23)
        self.assertEqual(second_page["pagination"]["total_count"], 23)
        self.assertEqual(
            [item["name"] for item in searched_page["items"]],
            ["新活動快取失效測試"],
        )

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


class EventParticipationTests(TestCase):
    def setUp(self):
        self.owner = get_user_model().objects.create_user(username="owner", password="test-password")
        self.member = get_user_model().objects.create_user(username="member", password="test-password")
        self.event = Event.objects.create(
            name="週末桌遊",
            code="TABLETOP",
            owner=self.owner,
            location="台北市",
            capacity=1,
        )

    def test_authenticated_user_can_register_once_and_cancel(self):
        self.client.force_login(self.member)
        register_url = reverse("chillme:event-register", kwargs={"event_id": self.event.id})

        self.client.post(register_url)
        self.client.post(register_url)

        self.assertEqual(Registration.objects.filter(event=self.event, user=self.member).count(), 1)
        response = self.client.post(reverse("chillme:event-cancel-registration", kwargs={"event_id": self.event.id}))
        self.assertRedirects(response, reverse("chillme:event-detail", kwargs={"event_id": self.event.id}))
        self.assertFalse(Registration.objects.filter(event=self.event, user=self.member).exists())

    def test_full_event_does_not_accept_another_registration(self):
        Registration.objects.create(event=self.event, user=self.owner, participant_name="owner")
        self.client.force_login(self.member)

        self.client.post(reverse("chillme:event-register", kwargs={"event_id": self.event.id}))

        self.assertFalse(Registration.objects.filter(event=self.event, user=self.member).exists())

    def test_dashboard_shows_owned_and_registered_events(self):
        joined_event = Event.objects.create(name="電影", code="MOVIE", owner=self.member)
        Registration.objects.create(event=joined_event, user=self.owner, participant_name="owner")
        self.client.force_login(self.owner)

        response = self.client.get(reverse("chillme:dashboard"))

        self.assertContains(response, self.event.name)
        self.assertContains(response, joined_event.name)

    def test_create_event_accepts_schedule_location_and_capacity(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("chillme:event-create"),
            {"name": "晨跑", "code": "RUN2026", "event_at": "2026-12-01T08:30", "location": "河濱公園", "capacity": "6", "description": "一起輕鬆跑"},
        )

        event = Event.objects.get(code="RUN2026")
        self.assertRedirects(response, reverse("chillme:event-detail", kwargs={"event_id": event.id}))
        self.assertEqual(event.location, "河濱公園")
        self.assertEqual(event.capacity, 6)

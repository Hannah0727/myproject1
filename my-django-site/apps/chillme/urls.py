
from django.urls import path

from .views import EventDetailView, EventListView

app_name = "chillme"

urlpatterns = [
    path(
        "events/",
        EventListView.as_view(),
        name="event-list"
    ),
    path(
        "events/<int:event_id>/",
        EventDetailView.as_view(),
        name="event-detail"
    ),
]


from django.urls import path

from .views import EventListView, EventDetailView, EventCreateView

app_name = "chillme"

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
]

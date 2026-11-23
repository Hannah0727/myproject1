
from django.urls import path

from .views import EventCreateView, EventDetailView, EventListDataView, EventListView

app_name = "chillme"

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/data/", EventListDataView.as_view(), name="event-list-data"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
]

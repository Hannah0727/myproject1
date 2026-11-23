
from django.urls import path

from .views import (
    DashboardView,
    EventCreateView,
    EventDetailView,
    EventListDataView,
    EventListView,
    EventRegistrationCancelView,
    EventRegistrationView,
)

app_name = "chillme"

urlpatterns = [
    path("events/", EventListView.as_view(), name="event-list"),
    path("events/data/", EventListDataView.as_view(), name="event-list-data"),
    path("events/create/", EventCreateView.as_view(), name="event-create"),
    path("events/<int:event_id>/", EventDetailView.as_view(), name="event-detail"),
    path("events/<int:event_id>/register/", EventRegistrationView.as_view(), name="event-register"),
    path("events/<int:event_id>/cancel-registration/", EventRegistrationCancelView.as_view(), name="event-cancel-registration"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
]

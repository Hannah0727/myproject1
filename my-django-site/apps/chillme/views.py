
from django.shortcuts import get_object_or_404, render
from django.views import View

from .models import Event


class EventDetailView(View):
    def get(self, request, event_id):
        event = get_object_or_404(Event, id=event_id)

        return render(
            request,
            "chillme/event_detail.html",
            {"event": event}
        )

class EventListView(View):
    def get(self, request):
        keyword = request.GET.get("q", "").strip()
        events = Event.objects.all()

        if keyword:
            events = events.filter(name__icontains=keyword)

        context = {
            "events": events,
            "keyword": keyword,
        }

        return render(
            request,
            "chillme/event_list.html",
            context
        )

from django.views.generic import TemplateView
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from apps.chillme.models import Event

class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        events = Event.objects.select_related("owner").prefetch_related("registrations")
        context["new_events"] = events[:3]
        context["upcoming_events"] = events.filter(event_at__isnull=False).order_by("event_at")[:3]
        return context
class TextResponseView(View):
    def get(self, request):
        return HttpResponse("這是一段由 HttpResponse 回傳的文字。")

class JsonResponseView(View):
    def get(self, request):
        return JsonResponse(
            {
                "message": "這是一份由 JsonResponse 回傳的資料。",
                "course": "Python 全端開發",
            },
            status=200,
        )


from django.shortcuts import redirect

class GoHomeView(View):
    def get(self, request):
        return redirect("core:home")

class GreetingView(View):
    def get(self, request):
        name = request.GET.get("name", "訪客")
        context = {"name": name}
        return render(request, "core/greeting.html", context)


from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View

from .models import Event, Tag


class EventDetailView(View):
    def get(self, request, event_id):
        event = get_object_or_404(
            Event.objects
            .select_related("line_group", "owner")
            .prefetch_related("registrations", "tags"),
            id=event_id,
        )
        return render(
            request,
            "chillme/event_detail.html",
            {"event": event}
        )


class EventListView(View):
    def get(self, request):
        keyword = request.GET.get("q", "").strip()
        events = Event.objects.select_related("owner")

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


class EventCreateView(LoginRequiredMixin, View):
    template_name = "chillme/event_create.html"

    def get(self, request):
        return render(
            request,
            self.template_name,
            {"tags": Tag.objects.all()}
        )

    def post(self, request):
        name = request.POST.get("name", "").strip()
        code = request.POST.get("code", "").strip()
        selected_tag_ids = request.POST.getlist("tags")

        context = {
            "tags": Tag.objects.all(),
            "name": name,
            "code": code,
            "selected_tag_ids": selected_tag_ids,
        }

        if not name or not code:
            context["error"] = "請填寫活動名稱與活動代碼。"
            return render(
                request,
                self.template_name,
                context,
                status=400
            )

        if len(name) > 100 or len(code) > 12:
            context["error"] = "活動名稱或活動代碼太長。"
            return render(
                request,
                self.template_name,
                context,
                status=400
            )

        if Event.objects.filter(code=code).exists():
            context["error"] = "這個活動代碼已經被使用，請更換。"
            return render(
                request,
                self.template_name,
                context,
                status=400
            )

        selected_tags = Tag.objects.filter(
            id__in=selected_tag_ids
        )

        event = Event.objects.create(
            name=name,
            code=code,
            owner=request.user,
        )

        event.tags.set(selected_tags)

        return redirect(
            "chillme:event-detail",
            event_id=event.id
        )

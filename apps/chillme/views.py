
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
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
            {"keyword": keyword}
        )


class EventListDataView(View):
    page_size = 20

    def get(self, request):
        keyword = request.GET.get("q", "").strip()
        events = Event.objects.select_related("owner")

        if keyword:
            events = events.filter(name__icontains=keyword)

        paginator = Paginator(events, self.page_size)
        requested_page = request.GET.get("page", 1)

        try:
            page = paginator.page(requested_page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        items = []
        for event in page.object_list:
            try:
                owner_name = event.owner.profile.display_name or event.owner.username
            except ObjectDoesNotExist:
                owner_name = event.owner.username

            items.append({
                "id": event.id,
                "name": event.name,
                "code": event.code,
                "owner_name": owner_name,
                "detail_url": reverse(
                    "chillme:event-detail",
                    kwargs={"event_id": event.id},
                ),
            })

        return JsonResponse({
            "items": items,
            "pagination": {
                "page": page.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
            },
            "query": keyword,
        })


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

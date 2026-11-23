
from hashlib import sha256

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View

from .models import Event, Registration, Tag


EVENT_LIST_CACHE_VERSION_KEY = "chillme:event-list:version"
EVENT_LIST_CACHE_KEY_PREFIX = "chillme:event-list:data-v2"


def get_event_list_cache_version():
    try:
        version = cache.get(EVENT_LIST_CACHE_VERSION_KEY)
        if version is None:
            cache.add(EVENT_LIST_CACHE_VERSION_KEY, 1)
            version = cache.get(EVENT_LIST_CACHE_VERSION_KEY, 1)
        return int(version)
    except Exception:
        return None


def advance_event_list_cache_version():
    try:
        if not cache.add(EVENT_LIST_CACHE_VERSION_KEY, 2):
            cache.incr(EVENT_LIST_CACHE_VERSION_KEY)
    except Exception:
        pass


def event_list_cache_key(version, keyword, page):
    keyword_hash = sha256(keyword.encode()).hexdigest()
    return f"{EVENT_LIST_CACHE_KEY_PREFIX}:v{version}:q{keyword_hash}:p{page}"


def normalized_requested_page(value):
    try:
        page = int(value)
    except (TypeError, ValueError):
        return None
    return page if page > 0 else None


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
            {
                "event": event,
                "is_registered": request.user.is_authenticated and event.registrations.filter(user=request.user).exists(),
                "is_full": event.capacity is not None and event.registrations.count() >= event.capacity,
            },
        )


class EventListView(View):
    def get(self, request):
        keyword = request.GET.get("q", "").strip()
        events = Event.objects.select_related("owner").annotate(
            registration_count=Count("registrations"),
        ).order_by("-created_at")

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
        requested_page = request.GET.get("page", 1)
        candidate_page = normalized_requested_page(requested_page)
        cache_version = get_event_list_cache_version()
        cache_key = None

        if cache_version is not None and candidate_page is not None:
            cache_key = event_list_cache_key(
                cache_version,
                keyword,
                candidate_page,
            )
            try:
                cached_payload = cache.get(cache_key)
            except Exception:
                cached_payload = None
            if cached_payload is not None:
                return JsonResponse(cached_payload)

        events = Event.objects.select_related("owner").annotate(
            registration_count=Count("registrations"),
        ).order_by("-created_at")

        if keyword:
            events = events.filter(name__icontains=keyword)

        paginator = Paginator(events, self.page_size)

        try:
            page = paginator.page(requested_page)
        except PageNotAnInteger:
            page = paginator.page(1)
        except EmptyPage:
            page = paginator.page(paginator.num_pages)

        resolved_cache_key = None
        if cache_version is not None:
            resolved_cache_key = event_list_cache_key(
                cache_version,
                keyword,
                page.number,
            )
            if resolved_cache_key != cache_key:
                try:
                    cached_payload = cache.get(resolved_cache_key)
                except Exception:
                    cached_payload = None
                if cached_payload is not None:
                    return JsonResponse(cached_payload)

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
                "event_at": event.event_at.isoformat() if event.event_at else None,
                "location": event.location,
                "capacity": event.capacity,
                "registration_count": event.registration_count,
                "detail_url": reverse(
                    "chillme:event-detail",
                    kwargs={"event_id": event.id},
                ),
            })

        payload = {
            "items": items,
            "pagination": {
                "page": page.number,
                "total_pages": paginator.num_pages,
                "total_count": paginator.count,
                "has_previous": page.has_previous(),
                "has_next": page.has_next(),
            },
            "query": keyword,
        }

        if resolved_cache_key is not None:
            try:
                cache.set(resolved_cache_key, payload)
            except Exception:
                pass

        return JsonResponse(payload)


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
        description = request.POST.get("description", "").strip()
        event_at = request.POST.get("event_at", "").strip()
        location = request.POST.get("location", "").strip()
        capacity = request.POST.get("capacity", "").strip()
        selected_tag_ids = request.POST.getlist("tags")

        context = {
            "tags": Tag.objects.all(),
            "name": name,
            "code": code,
            "description": description,
            "event_at": event_at,
            "location": location,
            "capacity": capacity,
            "selected_tag_ids": selected_tag_ids,
        }

        if not name or not code or not event_at or not location or not capacity:
            context["error"] = "請完整填寫活動名稱、代碼、時間、地點與人數上限。"
            return render(
                request,
                self.template_name,
                context,
                status=400
            )

        try:
            capacity_value = int(capacity)
        except ValueError:
            capacity_value = 0

        if len(name) > 100 or len(code) > 12 or len(location) > 150 or capacity_value < 1:
            context["error"] = "請確認欄位長度與人數上限（至少 1 人）。"
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

        from django.utils.dateparse import parse_datetime
        from django.utils import timezone
        event_at_value = parse_datetime(event_at)
        if event_at_value is None:
            context["error"] = "請輸入正確的活動時間。"
            return render(request, self.template_name, context, status=400)
        if timezone.is_naive(event_at_value):
            event_at_value = timezone.make_aware(event_at_value)

        event = Event.objects.create(
            name=name,
            code=code,
            owner=request.user,
            description=description,
            event_at=event_at_value,
            location=location,
            capacity=capacity_value,
        )

        event.tags.set(selected_tags)

        return redirect(
            "chillme:event-detail",
            event_id=event.id
        )


class EventRegistrationView(LoginRequiredMixin, View):
    def post(self, request, event_id):
        with transaction.atomic():
            event = get_object_or_404(Event.objects.select_for_update(), id=event_id)
            if event.capacity is not None and event.registrations.count() >= event.capacity:
                return redirect("chillme:event-detail", event_id=event.id)
            try:
                try:
                    participant_name = request.user.profile.display_name or request.user.username
                except ObjectDoesNotExist:
                    participant_name = request.user.username
                Registration.objects.create(
                    event=event,
                    user=request.user,
                    participant_name=participant_name,
                )
            except IntegrityError:
                pass
        return redirect("chillme:event-detail", event_id=event_id)


class EventRegistrationCancelView(LoginRequiredMixin, View):
    def post(self, request, event_id):
        Registration.objects.filter(event_id=event_id, user=request.user).delete()
        return redirect("chillme:event-detail", event_id=event_id)


class DashboardView(LoginRequiredMixin, View):
    def get(self, request):
        return render(
            request,
            "chillme/dashboard.html",
            {
                "owned_events": Event.objects.filter(owner=request.user).prefetch_related("registrations"),
                "registered_events": Event.objects.filter(registrations__user=request.user).distinct(),
            },
        )

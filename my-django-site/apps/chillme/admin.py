from django.contrib import admin
from .models import Event, LineGroup, Registration, Tag


@admin.register(LineGroup)
class LineGroupAdmin(admin.ModelAdmin):
    list_display = ("display_name", "group_id", "created_at")
    search_fields = ("display_name", "group_id")


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "line_group", "created_at")
    search_fields = ("name", "code")
    list_filter = ("created_at",)
    filter_horizontal = ("tags",)


@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ("participant_name", "event", "created_at")
    search_fields = ("participant_name", "event__name")
    list_filter = ("event",)
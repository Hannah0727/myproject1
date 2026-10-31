
from django.conf import settings
from django.db import models


class LineGroup(models.Model):
    group_id = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="LINE 群組 ID"
    )
    display_name = models.CharField(
        max_length=100,
        verbose_name="群組顯示名稱"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="建立時間"
    )

    class Meta:
        verbose_name = "LINE 群組"
        verbose_name_plural = "LINE 群組"

    def __str__(self):
        return self.display_name


class Tag(models.Model):
    name = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="標籤名稱"
    )

    class Meta:
        verbose_name = "活動標籤"
        verbose_name_plural = "活動標籤"

    def __str__(self):
        return self.name


class Event(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name="活動名稱"
    )
    code = models.CharField(
        max_length=12,
        unique=True,
        verbose_name="活動代碼"
    )

    # Week 7：記錄活動建立者
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_events",
        verbose_name="建立者",
    )

    line_group = models.OneToOneField(
        LineGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="event",
        verbose_name="LINE 群組",
    )
    tags = models.ManyToManyField(
        Tag,
        related_name="events",
        blank=True,
        verbose_name="活動標籤",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="建立時間"
    )

    class Meta:
        verbose_name = "揪團活動"
        verbose_name_plural = "揪團活動"
        ordering = ("-created_at",)

    def __str__(self):
        return self.name


class Registration(models.Model):
    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="registrations",
        verbose_name="所屬活動",
    )
    participant_name = models.CharField(
        max_length=100,
        verbose_name="報名者姓名",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="報名時間",
    )

    class Meta:
        verbose_name = "報名紀錄"
        verbose_name_plural = "報名紀錄"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.event.name}｜{self.participant_name}"

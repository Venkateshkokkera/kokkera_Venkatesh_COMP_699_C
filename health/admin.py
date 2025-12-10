from django.contrib import admin
from .models import HealthData, Notification
from django.utils.html import format_html
from django.urls import reverse

@admin.register(HealthData)
class HealthDataAdmin(admin.ModelAdmin):
    list_display = ("user", "date", "heart_rate", "bmi", "sleep_hours")
    list_filter = ("date", "user")

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "short_message", "is_read", "created_at")
    list_filter = ("is_read", "created_at")

    def short_message(self, obj):
        return obj.message[:60]
    short_message.short_description = "Message"

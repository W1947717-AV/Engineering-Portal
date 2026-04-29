from django.contrib import admin
from .models import Meeting


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'team',
        'organiser',
        'recipient',
        'status',
        'recurrence',
        'date',
        'time',
        'location',
    )

    list_filter = (
        'team',
        'status',
        'recurrence',
        'date',
    )

    search_fields = (
        'title',
        'team__name',
        'organiser__username',
        'recipient__username',
        'location',
    )
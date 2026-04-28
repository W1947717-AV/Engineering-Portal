from django.contrib import admin
from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'recipient', 'is_read', 'is_draft', 'created_at')
    list_filter = ('is_read', 'is_draft', 'created_at')
    search_fields = ('subject', 'body', 'sender__username', 'recipient__username')
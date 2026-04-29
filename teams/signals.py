from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE, DELETION
from .models import Team, Department


def log_change(user_id, obj, action_flag, message):
    """
    Helper to write an entry to Django's admin LogEntry table.
    Used to record front-end changes as well as admin changes.
    """
    LogEntry.objects.log_action(
        user_id=user_id,
        content_type_id=ContentType.objects.get_for_model(obj).pk,
        object_id=obj.pk,
        object_repr=str(obj),
        action_flag=action_flag,
        change_message=message,
    )
from django.db import models
from django.contrib.auth.models import User
from teams.models import Team


class Meeting(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    ]

    RECURRENCE_CHOICES = [
        ('none', 'One Time'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    title = models.CharField(max_length=150)

    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='meetings'
    )

    organiser = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='organised_meetings'
    )

    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='meeting_requests'
    )

    date = models.DateField()
    time = models.TimeField()
    location = models.CharField(max_length=150, blank=True)
    notes = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    recurrence = models.CharField(
        max_length=10,
        choices=RECURRENCE_CHOICES,
        default='none'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
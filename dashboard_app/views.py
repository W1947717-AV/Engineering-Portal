from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect

from teams.models import TeamMember
from messages_app.models import Message
from schedule_app.models import Meeting


@login_required(login_url='/login/')
def dashboard_home(request):
    my_memberships = (
        TeamMember.objects
        .filter(user=request.user)
        .select_related('team', 'team__department')
    )

    recent_messages = (
        Message.objects
        .filter(recipient=request.user, is_draft=False)
        .select_related('sender')
        .order_by('-created_at')[:5]
    )

    pending_requests = (
        Meeting.objects
        .filter(recipient=request.user, status='pending')
        .select_related('team', 'organiser')
        .order_by('date', 'time')
    )

    upcoming_meetings = (
        Meeting.objects
        .filter(
            Q(organiser=request.user) |
            Q(recipient=request.user, status='accepted')
        )
        .exclude(status='declined')
        .select_related('team', 'organiser', 'recipient')
        .order_by('date', 'time')[:5]
    )

    return render(request, 'dashboard_app/dashboard.html', {
        'my_memberships': my_memberships,
        'recent_messages': recent_messages,
        'pending_requests': pending_requests,
        'upcoming_meetings': upcoming_meetings,
    })


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('/register/')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/register/')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        login(request, user)
        return redirect('/dashboard/')

    return render(request, 'register.html')
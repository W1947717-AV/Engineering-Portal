# Author: Akhash Vivekanantha (W1947717)
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
    """
    Displays the main dashboard for the logged-in user.

    Aggregates four data sources:
    - my_memberships: teams the user belongs to
    - recent_messages: last 5 unread inbox messages
    - pending_requests: meeting requests awaiting the user's response
    - upcoming_meetings: next 5 accepted or pending meetings (as organiser or recipient)
    """
    # Teams the current user is a member of
    my_memberships = (
        TeamMember.objects
        .filter(user=request.user)
        .select_related('team', 'team__department')
    )

    # Last 5 received messages (not drafts), newest first
    recent_messages = (
        Message.objects
        .filter(recipient=request.user, is_draft=False)
        .select_related('sender')
        .order_by('-created_at')[:5]
    )

    # Meeting requests sent to the user that are still pending
    pending_requests = (
        Meeting.objects
        .filter(recipient=request.user, status='pending')
        .select_related('team', 'organiser')
        .order_by('date', 'time')
    )

    # Upcoming meetings: organised by user OR accepted as recipient
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
    """
    Handles new user self-registration.

    GET: Renders the registration form.
    POST: Validates that passwords match and the username is not taken,
          then creates the user, logs them in automatically, and redirects
          to the dashboard. Errors are passed back via Django's messages framework.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Validate passwords match before creating the user
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('/register/')

        # Prevent duplicate usernames
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('/register/')

        # create_user() hashes the password securely using PBKDF2
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
            email=email
        )

        # Log the user in immediately after registration
        login(request, user)
        return redirect('/dashboard/')

    return render(request, 'register.html')

@login_required(login_url='/login/')
def profile_update(request):
    """
    Allows the logged-in user to update their profile information.

    GET: Renders the profile form pre-filled with current details.
    POST: Updates first name, last name, and email, then redirects
          back to the profile page with a success message.
    """
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        user = request.user
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.save()

        messages.success(request, 'Profile updated successfully.')
        return redirect('/profile/')

    return render(request, 'profile.html')


@login_required(login_url='/login/')
def change_password(request):
    """
    Allows the logged-in user to change their password.

    GET: Renders the change password form.
    POST: Validates the current password, checks new passwords match,
          then updates and re-authenticates the user so they stay
          logged in after the change.
    """
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # Verify the current password is correct
        if not request.user.check_password(current_password):
            messages.error(request, 'Current password is incorrect.')
            return redirect('/change-password/')

        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('/change-password/')

        # Set new password — this hashes it securely
        request.user.set_password(new_password)
        request.user.save()

        # Re-authenticate so the session stays valid after password change
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, request.user)

        messages.success(request, 'Password changed successfully.')
        return redirect('/profile/')

    return render(request, 'change_password.html')
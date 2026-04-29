from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

from teams.models import Team
from .models import Meeting


@login_required(login_url='/login/')
def schedule_home(request):
    meetings = (
        Meeting.objects
        .select_related('team', 'organiser', 'recipient')
        .filter(
            Q(organiser=request.user) |
            Q(recipient=request.user, status__in=['pending', 'accepted'])
        )
        .order_by('date', 'time')
    )

    return render(request, 'schedule_app/schedule_home.html', {
        'meetings': meetings,
    })


@login_required(login_url='/login/')
def create_meeting(request):
    teams = Team.objects.all().order_by('name')
    users = User.objects.exclude(id=request.user.id).order_by(
        'first_name',
        'last_name',
        'username'
    )

    selected_team_id = request.GET.get('team', '')

    if request.method == 'POST':
        title = request.POST.get('title')
        team_id = request.POST.get('team')
        recipient_id = request.POST.get('recipient')
        date = request.POST.get('date')
        time = request.POST.get('time')
        location = request.POST.get('location')
        notes = request.POST.get('notes')
        recurrence = request.POST.get('recurrence', 'none')

        team = get_object_or_404(Team, id=team_id)
        recipient = get_object_or_404(User, id=recipient_id)

        Meeting.objects.create(
            title=title,
            team=team,
            organiser=request.user,
            recipient=recipient,
            date=date,
            time=time,
            location=location,
            notes=notes,
            recurrence=recurrence,
            status='pending'
        )

        return redirect('/schedule/')

    return render(request, 'schedule_app/create_meeting.html', {
        'teams': teams,
        'users': users,
        'selected_team_id': selected_team_id,
    })


@login_required(login_url='/login/')
def accept_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id, recipient=request.user)

    if request.method == 'POST':
        meeting.status = 'accepted'
        meeting.save()

    return redirect('/schedule/')


@login_required(login_url='/login/')
def decline_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id, recipient=request.user)

    if request.method == 'POST':
        meeting.status = 'declined'
        meeting.save()

    return redirect('/schedule/')


@login_required(login_url='/login/')
def delete_meeting(request, id):
    meeting = get_object_or_404(Meeting, id=id)

    if meeting.organiser != request.user and meeting.recipient != request.user:
        return redirect('/schedule/')

    if request.method == 'POST':
        meeting.delete()
        return redirect('/schedule/')

    return render(request, 'schedule_app/delete_meeting.html', {
        'meeting': meeting,
    })
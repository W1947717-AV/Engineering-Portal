from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from .models import Team, Department


def team_home(request):
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    team_leader_id = request.GET.get('team_leader', '')
    selected_workstream = request.GET.get('workstream', '')
    sort = request.GET.get('sort', '')

    teams = (
        Team.objects
        .select_related('department', 'team_leader')
        .prefetch_related(
            'downstream_dependencies',
            'upstream_dependencies',
            'members__user'
        )
        .all()
        .distinct()
    )

    departments = Department.objects.all()

    leader_teams = (
        Team.objects
        .exclude(team_leader__isnull=True)
        .select_related('team_leader')
        .order_by('team_leader__first_name', 'team_leader__last_name', 'team_leader__username')
    )

    team_leaders = []
    seen_ids = set()

    for team in leader_teams:
        user = team.team_leader
        if user and user.id not in seen_ids:
            team_leaders.append(user)
            seen_ids.add(user.id)

    workstreams = (
        Team.objects
        .exclude(workstream__isnull=True)
        .exclude(workstream__exact='')
        .values_list('workstream', flat=True)
        .distinct()
        .order_by('workstream')
    )

    if query:
        teams = teams.filter(
            Q(name__icontains=query) |
            Q(department__name__icontains=query) |
            Q(team_leader__first_name__icontains=query) |
            Q(team_leader__last_name__icontains=query) |
            Q(team_leader__username__icontains=query) |
            Q(workstream__icontains=query) |
            Q(skills__icontains=query) |
            Q(members__user__first_name__icontains=query) |
            Q(members__user__last_name__icontains=query) |
            Q(members__user__username__icontains=query)
        ).distinct()

    if department_id:
        teams = teams.filter(department_id=department_id)

    if team_leader_id:
        teams = teams.filter(team_leader_id=team_leader_id)

    if selected_workstream:
        teams = teams.filter(workstream=selected_workstream)

    if sort == 'az':
        teams = teams.order_by('name')
    elif sort == 'za':
        teams = teams.order_by('-name')

    context = {
        'teams': teams,
        'departments': departments,
        'team_leaders': team_leaders,
        'workstreams': workstreams,
        'query': query,
        'selected_department': department_id,
        'selected_team_leader': team_leader_id,
        'selected_workstream': selected_workstream,
        'selected_sort': sort,
    }

    return render(request, 'teams/team_home.html', context)


def team_detail(request, id):
    team = get_object_or_404(
        Team.objects
        .select_related('department', 'team_leader')
        .prefetch_related(
            'downstream_dependencies',
            'upstream_dependencies',
            'members__user'
        ),
        id=id
    )

    return render(request, 'teams/team_detail.html', {'team': team})


def departments_home(request):
    query = request.GET.get('q', '')

    departments = Department.objects.prefetch_related(
        'team_set__team_leader',
        'team_set__members__user'
    ).all()

    if query:
        departments = departments.filter(
            Q(name__icontains=query) |
            Q(team__name__icontains=query) |
            Q(team__workstream__icontains=query)
        ).distinct()

    return render(request, 'teams/departments.html', {
        'departments': departments,
        'query': query,
    })


def department_detail(request, id):
    department = get_object_or_404(Department, id=id)

    teams = (
        Team.objects
        .filter(department=department)
        .select_related('team_leader')
        .prefetch_related('members__user', 'downstream_dependencies')
        .order_by('name')
    )

    return render(request, 'teams/department_detail.html', {
        'department': department,
        'teams': teams,
    })
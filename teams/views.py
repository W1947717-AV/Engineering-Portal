from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.admin.models import LogEntry
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Team, Department


def team_home(request):
    """
    Displays the main teams directory page.

    Supports filtering by department, team leader, and workstream,
    as well as free-text search across team name, skills, members, etc.
    Results can be sorted alphabetically A-Z or Z-A.

    GET params: q (search), department (id), team_leader (id),
                workstream (str), sort (az|za)
    """
    query = request.GET.get('q', '')
    department_id = request.GET.get('department', '')
    team_leader_id = request.GET.get('team_leader', '')
    selected_workstream = request.GET.get('workstream', '')
    sort = request.GET.get('sort', '')

    # Use select_related and prefetch_related to avoid N+1 queries
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

    # Build a deduplicated list of team leaders for the filter dropdown
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

    # Get distinct non-empty workstreams for the filter dropdown
    workstreams = (
        Team.objects
        .exclude(workstream__isnull=True)
        .exclude(workstream__exact='')
        .values_list('workstream', flat=True)
        .distinct()
        .order_by('workstream')
    )

    # Free-text search across multiple fields using Q objects (OR logic)
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

    # Apply dropdown filters
    if department_id:
        teams = teams.filter(department_id=department_id)

    if team_leader_id:
        teams = teams.filter(team_leader_id=team_leader_id)

    if selected_workstream:
        teams = teams.filter(workstream=selected_workstream)

    # Apply sorting
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
    """
    Displays the detail page for a single team.

    Fetches the team by primary key, including its department,
    leader, members, and both upstream and downstream dependencies.
    Returns 404 if the team does not exist.
    """
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
    """
    Displays all departments with their associated teams.

    Supports free-text search across department name, team name,
    and workstream. Uses prefetch_related to load teams and members
    efficiently in a single query set.
    """
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
    """
    Displays the detail page for a single department.

    Lists all teams belonging to this department, ordered alphabetically,
    with their leaders, members, and downstream dependencies prefetched.
    Returns 404 if the department does not exist.
    """
    department = get_object_or_404(Department, id=id)

    # Fetch teams in this department, ordered by name
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


@login_required(login_url='/login/')
def audit_trail(request):
    """
    Displays a log of all recorded changes to teams and departments.
    Restricted to admin/staff users only. Non-staff users get a 403 error.

    Uses Django's built-in LogEntry model which records every
    create, update, and delete action performed via the admin panel.
    Ordered by most recent first, limited to the last 100 entries.
    """
    # Explicitly block non-superuser users with a 403 Forbidden response
    if not request.user.is_superuser:
        raise PermissionDenied

    logs = (
        LogEntry.objects
        .select_related('user', 'content_type')
        .order_by('-action_time')[:100]
    )

    return render(request, 'teams/audit_trail.html', {'logs': logs})
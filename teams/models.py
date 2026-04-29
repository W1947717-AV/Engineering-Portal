from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    team_leader = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leading_teams'
    )

    workstream = models.CharField(max_length=100, blank=True)
    skills = models.TextField(blank=True)

    skills = models.TextField(blank=True)

    # Links to the team's code repositories
    code_repositories = models.TextField(
        blank=True,
        help_text="GitHub/GitLab URLs, one per line"
    )

    logo = models.CharField(max_length=100, blank=True)

    downstream_dependencies = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='upstream_dependencies',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def get_team_leader_name(self):
        if self.team_leader:
            full_name = f"{self.team_leader.first_name} {self.team_leader.last_name}".strip()
            if full_name:
                return full_name
            return self.team_leader.username
        return "Not assigned"


class TeamMember(models.Model):
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='members'
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='team_memberships'
    )

    role = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        full_name = f"{self.user.first_name} {self.user.last_name}".strip()
        if full_name:
            return full_name
        return self.user.username
# Author: Akhash Vivekanantha (W1947717)
from django import forms
from django.contrib import admin
from django.contrib.auth.models import User

from .models import Team, Department, TeamMember


class TeamAdminForm(forms.ModelForm):
    team_leader = forms.ModelChoiceField(
        queryset=User.objects.all(),
        required=False
    )

    class Meta:
        model = Team
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['team_leader'].label_from_instance = self.user_full_name

    def user_full_name(self, user):
        full_name = f"{user.first_name} {user.last_name}".strip()
        if full_name:
            return full_name
        return user.username


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    form = TeamAdminForm
    list_display = ('name', 'department', 'display_team_leader', 'workstream')
    list_filter = ('department', 'workstream')
    search_fields = ('name', 'skills', 'workstream')
    filter_horizontal = ('downstream_dependencies',)

    def display_team_leader(self, obj):
        return obj.get_team_leader_name()

    display_team_leader.short_description = 'Team Leader'


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('display_member_name', 'team', 'role')
    list_filter = ('team',)
    search_fields = (
        'user__first_name',
        'user__last_name',
        'user__username',
        'team__name',
        'role',
    )

    def display_member_name(self, obj):
        return obj.get_full_name()

    display_member_name.short_description = 'Member'
# Author: Akhash Vivekanantha (W1947717)
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Department, Team, TeamMember


class DepartmentModelTest(TestCase):
    """Tests for the Department model."""

    def setUp(self):
        self.department = Department.objects.create(name="Platform Engineering")

    def test_department_str(self):
        """Department __str__ returns its name."""
        self.assertEqual(str(self.department), "Platform Engineering")

    def test_department_created(self):
        """Department is saved to the database correctly."""
        self.assertEqual(Department.objects.count(), 1)


class TeamModelTest(TestCase):
    """Tests for the Team model."""

    def setUp(self):
        self.department = Department.objects.create(name="Platform Engineering")
        self.leader = User.objects.create_user(
            username="jsmith", first_name="John", last_name="Smith", password="test123"
        )
        self.team = Team.objects.create(
            name="Backend Services",
            department=self.department,
            team_leader=self.leader,
            workstream="Core Infrastructure",
            skills="Python, Django, PostgreSQL",
        )

    def test_team_str(self):
        """Team __str__ returns its name."""
        self.assertEqual(str(self.team), "Backend Services")

    def test_get_team_leader_name_full(self):
        """Returns full name when first and last name are set."""
        self.assertEqual(self.team.get_team_leader_name(), "John Smith")

    def test_get_team_leader_name_no_leader(self):
        """Returns 'Not assigned' when team has no leader."""
        team = Team.objects.create(name="Orphan Team")
        self.assertEqual(team.get_team_leader_name(), "Not assigned")

    def test_get_team_leader_name_username_fallback(self):
        """Falls back to username when first/last name are blank."""
        user = User.objects.create_user(username="noname", password="test123")
        self.team.team_leader = user
        self.team.save()
        self.assertEqual(self.team.get_team_leader_name(), "noname")

    def test_downstream_dependency(self):
        """Teams can be linked as downstream dependencies."""
        other_team = Team.objects.create(name="Cloud Reliability")
        self.team.downstream_dependencies.add(other_team)
        self.assertIn(other_team, self.team.downstream_dependencies.all())

    def test_upstream_dependency_reverse(self):
        """Upstream dependency is the reverse of downstream."""
        other_team = Team.objects.create(name="Cloud Reliability")
        self.team.downstream_dependencies.add(other_team)
        self.assertIn(self.team, other_team.upstream_dependencies.all())


class TeamMemberModelTest(TestCase):
    """Tests for the TeamMember model."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="asmith", first_name="Alice", last_name="Smith", password="test123"
        )
        self.team = Team.objects.create(name="Backend Services")
        self.member = TeamMember.objects.create(
            team=self.team, user=self.user, role="Senior Engineer"
        )

    def test_member_str(self):
        """TeamMember __str__ returns the member's full name."""
        self.assertEqual(str(self.member), "Alice Smith")

    def test_get_full_name_fallback(self):
        """Falls back to username when no first/last name."""
        user = User.objects.create_user(username="noname2", password="test123")
        member = TeamMember.objects.create(team=self.team, user=user)
        self.assertEqual(member.get_full_name(), "noname2")


class TeamViewTest(TestCase):
    """Tests for teams views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="viewer", password="test123")
        self.dept = Department.objects.create(name="Platform Engineering")
        self.team = Team.objects.create(
            name="Backend Services",
            department=self.dept,
            workstream="Core",
            skills="Python",
        )

    def test_team_home_redirects_if_not_logged_in(self):
        """Team home is accessible without login (public view)."""
        response = self.client.get("/teams/")
        self.assertEqual(response.status_code, 200)

    def test_team_home_lists_teams(self):
        """Team home page shows all teams."""
        response = self.client.get("/teams/")
        self.assertContains(response, "Backend Services")

    def test_team_search_by_name(self):
        """Search filters teams by name."""
        response = self.client.get("/teams/?q=Backend")
        self.assertContains(response, "Backend Services")

    def test_team_search_no_results(self):
        """Search with no matches shows no teams."""
        response = self.client.get("/teams/?q=zzznomatch")
        self.assertNotContains(response, "Backend Services")

    def test_team_detail_page(self):
        """Team detail page returns 200 and shows team name."""
        response = self.client.get(f"/teams/{self.team.id}/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Backend Services")

    def test_team_detail_404_on_missing(self):
        """Team detail returns 404 for non-existent team."""
        response = self.client.get("/teams/9999/")
        self.assertEqual(response.status_code, 404)

    def test_departments_page(self):
        """Departments page returns 200 and lists department."""
        response = self.client.get("/teams/departments/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Platform Engineering")

    def test_department_filter(self):
        """Filtering by department only shows teams in that department."""
        other_dept = Department.objects.create(name="Mobile Products")
        response = self.client.get(f"/teams/?department={self.dept.id}")
        self.assertContains(response, "Backend Services")

    def test_sort_az(self):
        """Sort A-Z returns 200."""
        response = self.client.get("/teams/?sort=az")
        self.assertEqual(response.status_code, 200)
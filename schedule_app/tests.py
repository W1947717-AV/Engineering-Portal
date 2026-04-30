# Authors: Akhash Vivekanantha (W1947717), Safwan Choudhury
from django.test import TestCase, Client
from django.contrib.auth.models import User
from teams.models import Team, Department
from .models import Meeting


class MeetingModelTest(TestCase):
    """Tests for the Meeting model."""

    def setUp(self):
        self.dept = Department.objects.create(name="Platform")
        self.team = Team.objects.create(name="Backend Services", department=self.dept)
        self.organiser = User.objects.create_user(username="organiser", password="test123")
        self.recipient = User.objects.create_user(username="recipient", password="test123")
        self.meeting = Meeting.objects.create(
            title="Sprint Planning",
            team=self.team,
            organiser=self.organiser,
            recipient=self.recipient,
            date="2026-05-01",
            time="10:00:00",
        )

    def test_meeting_str(self):
        """Meeting __str__ returns its title."""
        self.assertEqual(str(self.meeting), "Sprint Planning")

    def test_meeting_default_status(self):
        """New meetings default to 'pending' status."""
        self.assertEqual(self.meeting.status, "pending")

    def test_meeting_default_recurrence(self):
        """New meetings default to 'none' recurrence."""
        self.assertEqual(self.meeting.recurrence, "none")


class MeetingViewTest(TestCase):
    """Tests for schedule views."""

    def setUp(self):
        self.client = Client()
        self.dept = Department.objects.create(name="Platform")
        self.team = Team.objects.create(name="Backend Services", department=self.dept)
        self.organiser = User.objects.create_user(username="organiser", password="test123")
        self.recipient = User.objects.create_user(username="recipient", password="test123")
        self.client.login(username="organiser", password="test123")

    def test_schedule_home_requires_login(self):
        """Schedule page redirects unauthenticated users."""
        self.client.logout()
        response = self.client.get("/schedule/")
        self.assertRedirects(response, "/login/?next=/schedule/")

    def test_schedule_home_loads(self):
        """Schedule home returns 200 for logged-in users."""
        response = self.client.get("/schedule/")
        self.assertEqual(response.status_code, 200)

    def test_create_meeting_get(self):
        """Create meeting page loads correctly."""
        response = self.client.get("/schedule/new/")
        self.assertEqual(response.status_code, 200)

    def test_create_meeting_post(self):
        """Posting to create meeting creates a Meeting object."""
        response = self.client.post("/schedule/new/", {
            "title": "Kickoff",
            "team": self.team.id,
            "recipient": self.recipient.id,
            "date": "2026-05-10",
            "time": "09:00",
            "location": "Zoom",
            "notes": "Bring your laptop",
            "recurrence": "none",
        })
        self.assertEqual(Meeting.objects.count(), 1)
        self.assertRedirects(response, "/schedule/")

    def test_accept_meeting(self):
        """Recipient can accept a pending meeting."""
        meeting = Meeting.objects.create(
            title="Review", team=self.team, organiser=self.organiser,
            recipient=self.recipient, date="2026-05-01", time="10:00"
        )
        self.client.login(username="recipient", password="test123")
        self.client.post(f"/schedule/{meeting.id}/accept/")
        meeting.refresh_from_db()
        self.assertEqual(meeting.status, "accepted")

    def test_decline_meeting(self):
        """Recipient can decline a pending meeting."""
        meeting = Meeting.objects.create(
            title="Review", team=self.team, organiser=self.organiser,
            recipient=self.recipient, date="2026-05-01", time="10:00"
        )
        self.client.login(username="recipient", password="test123")
        self.client.post(f"/schedule/{meeting.id}/decline/")
        meeting.refresh_from_db()
        self.assertEqual(meeting.status, "declined")

    def test_delete_meeting(self):
        """Organiser can delete a meeting."""
        meeting = Meeting.objects.create(
            title="Review", team=self.team, organiser=self.organiser,
            recipient=self.recipient, date="2026-05-01", time="10:00"
        )
        self.client.post(f"/schedule/{meeting.id}/delete/")
        self.assertEqual(Meeting.objects.count(), 0)

    def test_schedule_shows_upcoming_meetings(self):
        """Schedule home shows meetings for current user."""
        Meeting.objects.create(
            title="My Meeting", team=self.team, organiser=self.organiser,
            recipient=self.recipient, date="2026-05-01", time="10:00"
        )
        response = self.client.get("/schedule/")
        self.assertContains(response, "My Meeting")
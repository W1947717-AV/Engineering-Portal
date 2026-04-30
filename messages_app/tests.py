# Authors: Akhash Vivekanantha (W1947717), Gopishan Murukadasan
from django.test import TestCase, Client
from django.contrib.auth.models import User
from .models import Message


class MessageModelTest(TestCase):
    """Tests for the Message model."""

    def setUp(self):
        self.sender = User.objects.create_user(username="sender", password="test123")
        self.recipient = User.objects.create_user(username="recipient", password="test123")
        self.message = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject="Hello",
            body="Test body",
        )

    def test_message_str(self):
        """Message __str__ returns its subject."""
        self.assertEqual(str(self.message), "Hello")

    def test_message_defaults(self):
        """New messages default to unread and not draft."""
        self.assertFalse(self.message.is_read)
        self.assertFalse(self.message.is_draft)

    def test_draft_message(self):
        """Draft messages are stored with is_draft=True."""
        draft = Message.objects.create(
            sender=self.sender,
            recipient=self.recipient,
            subject="Draft",
            body="Not sent yet",
            is_draft=True,
        )
        self.assertTrue(draft.is_draft)


class MessageViewTest(TestCase):
    """Tests for messages views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="user1", password="test123")
        self.other = User.objects.create_user(username="user2", password="test123")
        self.client.login(username="user1", password="test123")

    def test_inbox_requires_login(self):
        """Inbox redirects unauthenticated users to login."""
        self.client.logout()
        response = self.client.get("/messages/inbox/")
        self.assertRedirects(response, "/login/?next=/messages/inbox/")

    def test_inbox_loads(self):
        """Inbox returns 200 for logged-in users."""
        response = self.client.get("/messages/inbox/")
        self.assertEqual(response.status_code, 200)

    def test_sent_loads(self):
        """Sent page returns 200."""
        response = self.client.get("/messages/sent/")
        self.assertEqual(response.status_code, 200)

    def test_drafts_loads(self):
        """Drafts page returns 200."""
        response = self.client.get("/messages/drafts/")
        self.assertEqual(response.status_code, 200)

    def test_new_message_get(self):
        """New message page loads correctly."""
        response = self.client.get("/messages/new/")
        self.assertEqual(response.status_code, 200)

    def test_send_message(self):
        """Sending a message creates a Message object."""
        response = self.client.post("/messages/new/", {
            "recipient": self.other.id,
            "subject": "Test Subject",
            "body": "Test body content",
            "action": "send",
        })
        self.assertEqual(Message.objects.filter(is_draft=False).count(), 1)
        self.assertRedirects(response, "/messages/sent/")

    def test_save_draft(self):
        """Saving as draft creates a draft message."""
        self.client.post("/messages/new/", {
            "recipient": self.other.id,
            "subject": "Draft Subject",
            "body": "Draft body",
            "action": "draft",
        })
        self.assertEqual(Message.objects.filter(is_draft=True).count(), 1)

    def test_view_message_marks_as_read(self):
        """Viewing a received message marks it as read."""
        message = Message.objects.create(
            sender=self.other,
            recipient=self.user,
            subject="Read me",
            body="Body",
        )
        self.client.get(f"/messages/{message.id}/")
        message.refresh_from_db()
        self.assertTrue(message.is_read)

    def test_inbox_shows_received_messages(self):
        """Inbox only shows messages sent to the current user."""
        Message.objects.create(sender=self.other, recipient=self.user, subject="For you", body="Hi")
        response = self.client.get("/messages/inbox/")
        self.assertContains(response, "For you")

    def test_inbox_search(self):
        """Inbox search filters by subject."""
        Message.objects.create(sender=self.other, recipient=self.user, subject="Unique123", body="Body")
        response = self.client.get("/messages/inbox/?q=Unique123")
        self.assertContains(response, "Unique123")
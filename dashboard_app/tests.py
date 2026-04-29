from django.test import TestCase, Client
from django.contrib.auth.models import User


class AuthViewTest(TestCase):
    """Tests for registration, login, logout, and dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", password="testpass123",
            first_name="Test", last_name="User"
        )

    def test_login_page_loads(self):
        """Login page returns 200."""
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        """Register page returns 200."""
        response = self.client.get("/register/")
        self.assertEqual(response.status_code, 200)

    def test_register_new_user(self):
        """Registering a new user creates account and redirects to dashboard."""
        response = self.client.post("/register/", {
            "username": "newuser",
            "first_name": "New",
            "last_name": "User",
            "password": "securepass123",
            "confirm_password": "securepass123",
        })
        self.assertTrue(User.objects.filter(username="newuser").exists())
        self.assertRedirects(response, "/dashboard/")

    def test_register_password_mismatch(self):
        """Mismatched passwords redirect back to register."""
        response = self.client.post("/register/", {
            "username": "baduser",
            "first_name": "Bad",
            "last_name": "User",
            "password": "password1",
            "confirm_password": "password2",
        })
        self.assertRedirects(response, "/register/")
        self.assertFalse(User.objects.filter(username="baduser").exists())

    def test_register_duplicate_username(self):
        """Duplicate username redirects back to register."""
        response = self.client.post("/register/", {
            "username": "testuser",
            "first_name": "Dup",
            "last_name": "User",
            "password": "test123",
            "confirm_password": "test123",
        })
        self.assertRedirects(response, "/register/")

    def test_login_valid_credentials(self):
        """Valid login redirects to dashboard."""
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "testpass123",
        })
        self.assertRedirects(response, "/dashboard/")

    def test_login_invalid_credentials(self):
        """Invalid credentials stay on login page."""
        response = self.client.post("/login/", {
            "username": "testuser",
            "password": "wrongpass",
        })
        self.assertEqual(response.status_code, 200)

    def test_dashboard_requires_login(self):
        """Dashboard redirects unauthenticated users to login."""
        response = self.client.get("/dashboard/")
        self.assertRedirects(response, "/login/?next=/dashboard/")

    def test_dashboard_loads_when_logged_in(self):
        """Dashboard returns 200 for authenticated users."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/dashboard/")
        self.assertEqual(response.status_code, 200)

    def test_dashboard_shows_username(self):
        """Dashboard greets the logged-in user by name."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get("/dashboard/")
        self.assertContains(response, "Test")

    def test_logout_redirects(self):
        """Logout redirects to login page."""
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post("/logout/")
        self.assertRedirects(response, "/login/")
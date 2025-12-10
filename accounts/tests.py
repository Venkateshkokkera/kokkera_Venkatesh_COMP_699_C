from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile

class ProfileSignalTest(TestCase):
    def test_profile_created_with_user(self):
        u = User.objects.create_user(username="testuser", password="pass123")
        self.assertTrue(hasattr(u, "profile"))
        self.assertIsInstance(u.profile, Profile)

class RegisterLoginTest(TestCase):
    def test_register_and_login(self):
        response = self.client.post("/accounts/register/", {
            "username": "u1", "email": "u1@example.com", "password": "pw1", "password_confirm": "pw1",
            "age": "30", "height_cm": "170", "weight_kg": "70"
        })
        # registration redirects to login
        self.assertEqual(response.status_code, 302)
        # now login
        login = self.client.post("/accounts/login/", {"username": "u1", "password": "pw1"})
        self.assertEqual(login.status_code, 302)

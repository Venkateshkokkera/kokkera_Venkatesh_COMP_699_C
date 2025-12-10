from django.test import TestCase
from django.contrib.auth.models import User
from .models import HealthData, Notification
from datetime import date, timedelta

class HealthFlowTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u2", password="pw2")
        # create 8 days of historical records
        for i in range(1, 9):
            HealthData.objects.create(user=self.user, date=date.today() - timedelta(days=i+1),
                                      heart_rate=70+i, bmi=22.0, sleep_hours=7.0)

    def test_create_today_and_risk(self):
        self.client.login(username="u2", password="pw2")
        resp = self.client.post("/log/", {
            "date": date.today().isoformat(),
            "heart_rate": 120, "bmi": 31.0, "sleep_hours": "4.5", "notes": "feeling bad"
        })
        self.assertEqual(resp.status_code, 302)  # redirect to dashboard
        # risk report should be available
        r = self.client.get("/risk-report/")
        self.assertContains(r, "Risk Level")

    def test_csv_export_requires_login(self):
        resp = self.client.get("/export/csv/")
        self.assertEqual(resp.status_code, 302)  # redirect to login
        self.client.login(username="u2", password="pw2")
        resp2 = self.client.get("/export/csv/")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.get("Content-Type"), "text/csv")

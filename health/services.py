from datetime import date, timedelta
from django.db.models import Avg
from .models import HealthData, Notification
from django.contrib.auth.models import User
import math

def compute_risk_and_generate_alerts(user: User):
    """
    A simple rule-based predictive engine:
    - Use last 14 days' average heart_rate and BMI.
    - If today's HR deviates > 15% from avg -> High risk.
    - If BMI > 30 -> Elevated risk.
    - Combine rules into a final risk score and message list.
    Returns: dict {risk_level, score (0-100), details:[]}
    """
    today = date.today()
    start = today - timedelta(days=14)
    entries = HealthData.objects.filter(user=user, date__gte=start, date__lt=today).order_by("date")
    result = {"risk_level": "Unknown", "score": 0, "details": []}

    if entries.count() < 7:
        result["risk_level"] = "Unknown"
        result["details"].append("Insufficient historical data (need >=7 days).")
        return result

    avg_hr = entries.aggregate(avg_hr=Avg("heart_rate"))["avg_hr"] or 0
    avg_bmi = entries.aggregate(avg_bmi=Avg("bmi"))["avg_bmi"] or 0

    latest = HealthData.objects.filter(user=user, date=today).first()
    if not latest:
        result["risk_level"] = "Unknown"
        result["details"].append("No entry for today.")
        return result

    # heart rate deviation
    deviation = 0.0
    if avg_hr > 0:
        deviation = abs(latest.heart_rate - avg_hr) / avg_hr

    score = 0
    if deviation > 0.15:
        score += 50
        result["details"].append(f"Heart rate deviated {deviation*100:.1f}% from 2-week avg.")
        Notification.objects.create(user=user, message=f"Heart rate deviated {deviation*100:.1f}% from 2-week avg.")
    else:
        score += int((1 - deviation) * 20)  # minor contribution

    # BMI based
    if latest.bmi >= 30:
        score += 30
        result["details"].append(f"BMI {latest.bmi:.1f} indicates obesity risk.")
        Notification.objects.create(user=user, message=f"BMI {latest.bmi:.1f} indicates obesity risk.")
    elif latest.bmi >= 25:
        score += 15
        result["details"].append(f"BMI {latest.bmi:.1f} indicates overweight.")

    # Sleep contribution (low sleep increases risk)
    if latest.sleep_hours < 5:
        score += 20
        result["details"].append(f"Low sleep: {latest.sleep_hours} hours.")
        Notification.objects.create(user=user, message=f"Low sleep reported: {latest.sleep_hours} hours.")

    # clamp score
    score = min(100, max(0, score))
    result["score"] = score

    if score >= 70:
        result["risk_level"] = "High"
    elif score >= 30:
        result["risk_level"] = "Medium"
    else:
        result["risk_level"] = "Low"

    return result

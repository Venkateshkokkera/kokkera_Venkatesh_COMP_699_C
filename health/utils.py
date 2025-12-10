import csv
from io import BytesIO
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from statistics import mean
from .models import HealthData


# =====================================================================
# 1️⃣ RISK PREDICTION ALGORITHM (NEW)
# =====================================================================
def calculate_risk(user):
    """
    Produces a risk prediction using the last 7 days of data.
    Rule-based scoring:
    - HR high → higher risk
    - Sleep low → higher risk
    - BMI abnormal → higher risk
    """

    records = HealthData.objects.filter(user=user).order_by("-date")[:7]

    if len(records) < 7:
        return {
            "risk_level": "Unknown",
            "score": 0,
            "details": ["Not enough data: Need at least 7 days of records."]
        }

    hr_values = [r.heart_rate for r in records]
    sleep_values = [r.sleep_hours for r in records]
    bmi_values = [r.bmi for r in records]

    avg_hr = mean(hr_values)
    avg_sleep = mean(sleep_values)
    avg_bmi = mean(bmi_values)

    score = 0
    details = []

    # Heart Rate
    if avg_hr > 100:
        score += 40
        details.append(f"High average heart rate ({avg_hr:.1f} bpm).")
    elif avg_hr > 90:
        score += 20
        details.append(f"Slightly elevated heart rate ({avg_hr:.1f} bpm).")

    # Sleep Hours
    if avg_sleep < 6:
        score += 30
        details.append(f"Low sleep ({avg_sleep:.1f} hours).")
    elif avg_sleep < 7:
        score += 10
        details.append(f"Slightly insufficient sleep ({avg_sleep:.1f} hours).")

    # BMI
    if avg_bmi < 18.5 or avg_bmi > 29.9:
        score += 20
        details.append(f"BMI outside healthy range ({avg_bmi:.1f}).")

    # Assign Risk Category
    if score >= 60:
        risk_level = "High"
    elif score >= 30:
        risk_level = "Medium"
    else:
        risk_level = "Low"

    return {
        "risk_level": risk_level,
        "score": score,
        "details": details,
    }


# =====================================================================
# 2️⃣ EXPORT CSV FUNCTION (Your original code)
# =====================================================================
def export_health_csv(user):
    records = HealthData.objects.filter(user=user).order_by("date")

    output = []
    headers = ["date", "heart_rate", "bmi", "sleep_hours", "notes", "created_at"]
    output.append(headers)

    for r in records:
        output.append([
            r.date.isoformat(),
            r.heart_rate,
            r.bmi,
            r.sleep_hours,
            r.notes,
            r.created_at.isoformat()
        ])

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = "attachment; filename=health_records.csv"

    writer = csv.writer(response)
    for row in output:
        writer.writerow(row)

    return response


# =====================================================================
# 3️⃣ EXPORT RISK REPORT AS PDF (Updated to use calculate_risk output)
# =====================================================================
def export_risk_pdf(user, risk_result=None):
    """
    Generates a PDF risk report.
    If risk_result is not passed, automatically computes it.
    """

    if risk_result is None:
        risk_result = calculate_risk(user)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flow = []

    # Title
    flow.append(Paragraph(f"Risk Report - {user.username}", styles["Title"]))
    flow.append(Spacer(1, 12))

    # Summary
    flow.append(Paragraph(f"Risk Level: {risk_result.get('risk_level')}", styles["Heading2"]))
    flow.append(Paragraph(f"Risk Score: {risk_result.get('score')}", styles["Normal"]))
    flow.append(Spacer(1, 12))

    # Details
    flow.append(Paragraph("Details:", styles["Heading3"]))
    for d in risk_result.get("details", []):
        flow.append(Paragraph(f"- {d}", styles["Normal"]))

    flow.append(Spacer(1, 12))

    # Latest 7 Records
    records = HealthData.objects.filter(user=user).order_by("-date")[:7]
    data = [["Date", "Heart Rate", "BMI", "Sleep (hrs)"]]

    for r in records:
        data.append([
            r.date.isoformat(),
            r.heart_rate,
            f"{r.bmi:.1f}",
            r.sleep_hours
        ])

    tbl = Table(data)
    flow.append(tbl)

    doc.build(flow)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=risk_report.pdf"

    return response

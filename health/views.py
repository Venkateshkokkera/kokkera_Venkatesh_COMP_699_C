from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse

from .models import HealthData, Notification
from .forms import HealthDataForm

# NEW: import your prediction algorithm
from .utils import calculate_risk, export_health_csv, export_risk_pdf


# ------------------------------------------------------------
# DASHBOARD — now uses calculate_risk()
# ------------------------------------------------------------
@login_required
def dashboard(request):
    user = request.user

    # Fetch records
    records = HealthData.objects.filter(user=user).order_by("-date")[:14]

    # Fetch notifications
    notifications = Notification.objects.filter(user=user).order_by("-created_at")[:10]

    # NEW: compute prediction result
    risk_result = calculate_risk(user)

    context = {
        "records": records,
        "notifications": notifications,
        "risk": risk_result,
    }
    return render(request, "health/dashboard.html", context)


# ------------------------------------------------------------
# CREATE HEALTH ENTRY
# ------------------------------------------------------------
@login_required
def health_create(request):
    if request.method == "POST":
        form = HealthDataForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.user = request.user
            try:
                obj.save()
            except Exception:
                messages.error(request, "Record for this date already exists.")
                return redirect("health:health_create")

            messages.success(request, "Health data saved.")
            return redirect("health:dashboard")
    else:
        form = HealthDataForm()

    return render(request, "health/health_form.html", {"form": form})


# ------------------------------------------------------------
# LIST HEALTH DATA
# ------------------------------------------------------------
@login_required
def health_list(request):
    records = HealthData.objects.filter(user=request.user).order_by("-date")
    return render(request, "health/health_list.html", {"records": records})


# ------------------------------------------------------------
# UPDATE RECORD
# ------------------------------------------------------------
@login_required
def health_update(request, pk):
    record = get_object_or_404(HealthData, pk=pk, user=request.user)

    if request.method == "POST":
        form = HealthDataForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Record updated.")
            return redirect("health:health_list")
    else:
        form = HealthDataForm(instance=record)

    return render(request, "health/health_form.html", {"form": form, "edit": True})


# ------------------------------------------------------------
# DELETE RECORD
# ------------------------------------------------------------
@login_required
def health_delete(request, pk):
    record = get_object_or_404(HealthData, pk=pk, user=request.user)

    if request.method == "POST":
        record.delete()
        messages.success(request, "Record deleted.")
        return redirect("health:health_list")

    return render(request, "health/health_delete_confirm.html", {"record": record})


# ------------------------------------------------------------
# RISK REPORT PAGE — uses new algorithm
# ------------------------------------------------------------
@login_required
def risk_report(request):
    risk_result = calculate_risk(request.user)
    return render(request, "health/risk_report.html", {"result": risk_result})


# ------------------------------------------------------------
# EXPORT CSV
# ------------------------------------------------------------
@login_required
def export_csv(request):
    return export_health_csv(request.user)


# ------------------------------------------------------------
# EXPORT PDF — uses new prediction engine
# ------------------------------------------------------------
@login_required
def export_pdf(request):
    risk_result = calculate_risk(request.user)
    return export_risk_pdf(request.user, risk_result)


# ------------------------------------------------------------
# MARK NOTIFICATION READ
# ------------------------------------------------------------
@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return redirect("health:dashboard")

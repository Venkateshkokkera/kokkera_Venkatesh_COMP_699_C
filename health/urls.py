from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("log/", views.health_create, name="health_create"),
    path("records/", views.health_list, name="health_list"),
    path("records/<int:pk>/edit/", views.health_update, name="health_update"),
    path("records/<int:pk>/delete/", views.health_delete, name="health_delete"),
    path("risk-report/", views.risk_report, name="risk_report"),
    path("export/csv/", views.export_csv, name="export_csv"),
    path("export/pdf/", views.export_pdf, name="export_pdf"),
    path("notification/<int:pk>/read/", views.mark_notification_read, name="mark_notification_read"),
]

from django.urls import path
from .views import AuditLogsView

urlpatterns = [path("audit_logs/", AuditLogsView, name="audit_logs")]

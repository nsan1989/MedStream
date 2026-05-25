from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import AuditLog


# Create your views here.
@login_required
def AuditLogsView(request):

    user = request.user

    queryset = AuditLog.objects.select_related("user", "organization").order_by(
        "-created_at"
    )

    if hasattr(user, "organization") and user.organization:
        queryset = queryset.filter(organization=user.organization)

    action = request.GET.get("action")
    target_model = request.GET.get("target_model")
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")

    if action:
        queryset = queryset.filter(action__icontains=action)

    if target_model:
        queryset = queryset.filter(target_model__icontains=target_model)

    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)

    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "action": action,
        "target_model": target_model,
        "date_from": date_from,
        "date_to": date_to,
    }

    return render(request, "audit_log/audit_logs.html", context)

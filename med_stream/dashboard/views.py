from django.shortcuts import render


# Dashboard view.
def DashboardView(request):
    context = {}
    return render(request, "dashboard/dashboard.html", context)

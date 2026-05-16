from django.shortcuts import render


# Base view.
def Home(request):
    context = {}
    return render(request, "core/home.html", context)


# Add department view.
def AddDepartment(request):
    context = {}
    return render(request, "core/add_department.html", context)

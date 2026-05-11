from django.shortcuts import render


# Base view.
def Home(request):
    context = {}
    return render(request, "core/home.html", context)

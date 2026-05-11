from django.shortcuts import render


# Base view.
def index(request):
    context = {}
    return render(request, "core/index.html", context)

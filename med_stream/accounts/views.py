from django.shortcuts import render


# Auth view.
def authView(request):
    context = {}
    return render(request, "accounts/auth.html", context)

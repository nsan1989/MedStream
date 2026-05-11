from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login


# Auth view.
def authView(request):
    context = {}
    return render(request, "accounts/auth.html", context)

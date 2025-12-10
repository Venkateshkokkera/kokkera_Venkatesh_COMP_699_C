from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProfileForm
from django.contrib import messages

def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        pform = ProfileForm(request.POST)

        if form.is_valid() and pform.is_valid():

            # Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # Update auto-created profile
            profile = user.profile
            profile.age = pform.cleaned_data["age"]
            profile.height_cm = pform.cleaned_data["height_cm"]
            profile.weight_kg = pform.cleaned_data["weight_kg"]
            profile.save()

            messages.success(request, "Account created. Please log in.")
            return redirect("accounts:login")

    else:
        form = UserRegisterForm()
        pform = ProfileForm()

    return render(request, "accounts/register.html", {"form": form, "pform": pform})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("health:dashboard")
        else:
            messages.error(request, "Invalid credentials.")
    return render(request, "accounts/login.html")

@login_required
def profile_view(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("health:dashboard")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "accounts/profile.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("accounts:login")

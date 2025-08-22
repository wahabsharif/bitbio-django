from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app_users.forms import UserRegistrationForm, UserLoginForm
from app_users.models import User
from app_users.views import approved_user_required


def home(request):
    """Home page view"""
    context = {}
    if request.user.is_authenticated:
        if request.user.status == "approved":
            context["user"] = request.user
            return render(request, "home.html", context)
        else:
            # User is authenticated but not approved, redirect to account with message
            messages.error(
                request,
                "Access denied. Your account is not approved. Please contact support.",
            )
            return redirect("account")
    else:
        # User is not authenticated, redirect to login
        return redirect("account")


def account(request):
    """Handle user login"""
    if request.method == "POST":
        print(f"DEBUG: POST request received with data: {request.POST}")
        form = UserLoginForm(request.POST)
        print(f"DEBUG: Form is valid: {form.is_valid()}")
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            print(f"DEBUG: Form data - Email: {email}, Password: {password}")
            print(f"DEBUG: Attempting to authenticate user: {email}")
            user = authenticate(request, username=email, password=password)
            print(f"DEBUG: Authentication result: {user}")

            if user is not None:
                if user.is_active:
                    # Check user status before allowing access
                    if user.status == "approved":
                        login(request, user)
                        messages.success(request, f"Welcome back, {user.first_name}!")
                        print(
                            f"DEBUG: User {user.email} logged in successfully, redirecting to calculator"
                        )
                        return redirect("calculator:calculator")
                    elif user.status == "pending":
                        messages.error(
                            request,
                            "Your account is pending approval. Please wait for admin approval before accessing the calculator.",
                        )
                    elif user.status == "rejected":
                        messages.error(
                            request,
                            "Your account has been rejected. Please contact support for more information.",
                        )
                    else:
                        messages.error(
                            request,
                            "Your account status is unknown. Please contact support.",
                        )
                else:
                    messages.error(
                        request, "Your account is not active. Please contact support."
                    )
            else:
                # Check if user exists but authentication failed
                try:
                    user = User.objects.get(email__iexact=email)
                    if user.check_password(password):
                        # Password is correct but user might not be approved
                        if user.status == "pending":
                            messages.error(
                                request,
                                "Your account is pending approval. Please wait for admin approval before logging in.",
                            )
                        elif user.status == "rejected":
                            messages.error(
                                request,
                                "Your account has been rejected. Please contact support for more information.",
                            )
                        else:
                            messages.error(request, "Invalid email or password.")
                    else:
                        messages.error(request, "Invalid email or password.")
                except User.DoesNotExist:
                    messages.error(request, "Invalid email or password.")
        else:
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = UserLoginForm()

    context = {
        "form": form,
    }
    return render(request, "account.html", context)


def registration(request):
    """Handle user registration from main URL"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # User needs approval
            user.save()

            from django.contrib import messages

            messages.success(
                request, "Registration successful! Your account is pending approval."
            )
            return redirect("registration_success")
        else:
            from django.contrib import messages

            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    from .countries import COUNTRIES

    context = {
        "form": form,
        "countries": COUNTRIES,
    }
    return render(request, "registration.html", context)


def registration_success(request):
    """Display success message after registration"""
    return render(request, "registration_success.html")


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("account")

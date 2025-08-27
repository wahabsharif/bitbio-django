from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from app_users.forms import UserRegistrationForm, UserLoginForm
from app_users.models import User
from app_users.views import approved_user_required
from app_users.domain_management import should_auto_approve, get_email_domain


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
                        messages.warning(
                            request,
                            "Your account is pending approval. Please wait for admin approval before you can access the system. You will receive an email notification once your account is approved.",
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
                            messages.warning(
                                request,
                                "Your account is pending approval. Please wait for admin approval before you can log in. You will receive an email notification once your account is approved.",
                            )
                        elif user.status == "rejected":
                            messages.error(
                                request,
                                "Your account has been rejected. Please contact support for more information.",
                            )
                        else:
                            messages.error(request, "Invalid email or password.")
                    else:
                        # Incorrect password for existing account
                        messages.error(request, "Incorrect password.")
                        form.add_error("password", "Incorrect password.")
                except User.DoesNotExist:
                    # Email not found
                    messages.error(request, "No account found with that email.")
                    form.add_error("email", "No account found with that email.")
        else:
            print(f"DEBUG: Form errors: {form.errors}")
    else:
        form = UserLoginForm()

    context = {
        "form": form,
    }
    return render(request, "account.html", context)


def registration(request):
    """Handle user registration with domain-based auto-approval"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user first (this will set default values)
            user = form.save()

            # Now check if user should be auto-approved based on email domain
            auto_approve = should_auto_approve(user.email)

            # Debug output to understand the flow
            print(
                f"DEBUG Registration: Email='{user.email}', Auto approve={auto_approve}"
            )
            domain = get_email_domain(user.email)
            print(f"DEBUG Registration: Domain='{domain}'")

            # Clear any existing messages before adding registration message
            storage = messages.get_messages(request)
            storage.used = True

            if auto_approve:
                # Update the user status and save again
                user.status = "approved"
                user.is_active = True
                user.save()

                messages.success(
                    request,
                    f"Your account has been automatically approved! You can now sign in with {user.email}.",
                )
            else:
                # Update the user status and save again
                user.is_active = False  # User needs manual approval
                user.save()

                messages.success(
                    request,
                    "Registration successful! Your account is pending approval. "
                    "You will receive an email notification once your account is approved.",
                )

            # Pass registration status via session
            request.session["registration_auto_approved"] = auto_approve
            request.session["registration_email"] = user.email
            return redirect("registration_success")
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserRegistrationForm()

    # Get countries list for the template
    from .countries import COUNTRIES

    context = {
        "form": form,
        "countries": COUNTRIES,
    }
    return render(request, "registration.html", context)


def registration_success(request):
    """Display success message after registration"""
    # Clear the session variables after displaying them
    if "registration_auto_approved" in request.session:
        del request.session["registration_auto_approved"]
    if "registration_email" in request.session:
        del request.session["registration_email"]

    return render(request, "registration_success.html")


def logout_view(request):
    """Handle user logout"""
    logout(request)
    messages.success(request, "You have been successfully logged out.")
    return redirect("account")

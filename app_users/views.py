from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from functools import wraps
from .forms import UserRegistrationForm, UserProfileUpdateForm
from .models import User
from .domain_management import should_auto_approve, get_email_domain
from django.contrib.auth import update_session_auth_hash


def approved_user_required(view_func):
    """
    Decorator to check if the user is approved.
    Redirects to account page with error message if not approved.
    """

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.status == "approved":
                return view_func(request, *args, **kwargs)
            else:
                messages.error(
                    request,
                    "Access denied. Your account is not approved. Please contact support.",
                )
                return redirect("account")
        else:
            return redirect("account")

    return _wrapped_view


def registration_view(request):
    """Handle user registration"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user first (this will set default values)
            user = form.save()

            # Now check if user should be auto-approved based on email domain
            auto_approve = should_auto_approve(user.email)

            from .domain_management import get_email_domain

            domain = get_email_domain(user.email)

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
                    "Registration successful! Your account is pending approval. ",
                )

            return redirect("registration_success")
        # Form has errors, but we don't need to add a general error message
        # since field-specific errors will be displayed below each field
    else:
        form = UserRegistrationForm()

    # Get countries list for the template
    from bitbio.countries import COUNTRIES

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


@login_required
def update_profile(request):
    """Update basic user profile fields via AJAX or standard POST"""
    if request.method == "POST":
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            # Detect if password is changing by comparing fields
            new_pw1 = form.cleaned_data.get("new_password1")
            user = form.save()
            if new_pw1:
                # Keep the user logged in after password change
                update_session_auth_hash(request, user)
            # AJAX request
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": True})
            messages.success(request, "Profile updated successfully.")
            return redirect("account")
        else:
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse(
                    {"success": False, "errors": form.errors}, status=400
                )
            messages.error(request, "Please correct the errors below.")
            return redirect("account")
    # For non-POST, return current data (AJAX only)
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        user = request.user
        billing = user.get_billing_info()
        shipping = user.get_shipping_info()
        return JsonResponse(
            {
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "job_title": user.job_title,
                "institution_tax_vat": user.institution_tax_vat,
                "in_vitro": user.in_vitro,
                "in_vivo": user.in_vivo,
                "communications_agreement": user.communications_agreement,
                "billing": billing,
                "shipping": shipping,
            }
        )
    return redirect("account")


class UserRegistrationView(CreateView):
    """Class-based view for user registration"""

    model = User
    form_class = UserRegistrationForm
    template_name = "registration.html"
    success_url = reverse_lazy("registration_success")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get countries list for the template
        from bitbio.countries import COUNTRIES

        context["countries"] = COUNTRIES
        return context

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # User needs approval
        user.save()

        messages.success(
            self.request, "Registration successful! Your account is pending approval."
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)

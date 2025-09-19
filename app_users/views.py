from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden, JsonResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from functools import wraps
from .forms import UserRegistrationForm, UserProfileUpdateForm
from .models import User
from .domain_management import should_auto_approve, get_email_domain
from django.contrib.auth import update_session_auth_hash


def send_verification_email(user, request):
    """Send email verification email to user"""
    import logging
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    logger = logging.getLogger(__name__)

    try:
        # Generate a new verification token
        user.generate_verification_token()

        # Build verification URL
        verification_url = request.build_absolute_uri(
            f"/users/verify-email/{user.email_verification_token}/"
        )

        # Build logo URL dynamically based on current domain
        logo_url = request.build_absolute_uri("/static/images/bitbio-logo.png")

        # Prepare email context
        context = {
            "user": user,
            "verification_url": verification_url,
            "site_name": "Bit.bio",
            "logo_url": logo_url,
        }

        # Render email templates
        html_message = render_to_string("emails/email_verification.html", context)
        plain_message = render_to_string("emails/email_verification.txt", context)

        # Log email attempt with detailed configuration
        logger.info(f"Attempting to send verification email to {user.email}")
        logger.info(f"Email backend: {settings.EMAIL_BACKEND}")
        logger.info(f"Email host: {settings.EMAIL_HOST}")
        logger.info(f"Email port: {settings.EMAIL_PORT}")
        logger.info(f"Email SSL: {settings.EMAIL_USE_SSL}")
        logger.info(f"Email TLS: {settings.EMAIL_USE_TLS}")
        logger.info(f"From email: {settings.DEFAULT_FROM_EMAIL}")
        logger.info(f"Verification URL: {verification_url}")

        # Test SMTP connection first
        try:
            if settings.EMAIL_USE_SSL:
                server = smtplib.SMTP_SSL(
                    settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30
                )
            else:
                server = smtplib.SMTP(
                    settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=30
                )
                if settings.EMAIL_USE_TLS:
                    server.starttls()

            server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            server.quit()
            logger.info("SMTP connection test successful")
        except Exception as smtp_error:
            logger.error(f"SMTP connection test failed: {smtp_error}")
            return False

        # Send email using Django's send_mail
        result = send_mail(
            subject="Verify your email address - Bit.bio",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        logger.info(f"Email sent successfully to {user.email}. Result: {result}")
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"SMTP Authentication failed for {user.email}: {e}")
        logger.error(
            "Check email credentials and ensure 'Less secure app access' is enabled for Gmail"
        )
        return False
    except smtplib.SMTPRecipientsRefused as e:
        logger.error(f"SMTP Recipients refused for {user.email}: {e}")
        return False
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"SMTP Server disconnected for {user.email}: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")
        logger.error(
            f"Email configuration - Backend: {settings.EMAIL_BACKEND}, Host: {settings.EMAIL_HOST}, User: {settings.EMAIL_HOST_USER}"
        )
        import traceback

        logger.error(f"Traceback: {traceback.format_exc()}")
        return False


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
            print(f"DEBUG: User created: {user.email}")
            print(
                f"DEBUG: User verification fields - is_email_verified: {user.is_email_verified}, token: {user.email_verification_token}, sent_at: {user.email_verification_sent_at}"
            )

            # Send email verification
            try:
                email_sent = send_verification_email(user, request)
                print(f"DEBUG: Email sending result: {email_sent}")
            except Exception as e:
                print(f"DEBUG: Error sending verification email: {e}")
                import traceback

                traceback.print_exc()
                email_sent = False

            # Debug: Check user state after email sending
            user.refresh_from_db()
            print(
                f"DEBUG: User after email sending - is_email_verified: {user.is_email_verified}, token: {user.email_verification_token}, sent_at: {user.email_verification_sent_at}"
            )

            # Now check if user should be auto-approved based on email domain
            auto_approve = should_auto_approve(user.email)

            from .domain_management import get_email_domain

            domain = get_email_domain(user.email)

            if auto_approve:
                # Update the user status and save again
                user.status = "approved"
                user.is_active = True
                user.save()

                # Set session variables for success template
                request.session["registration_auto_approved"] = True
                request.session["registration_email"] = user.email
                request.session["email_verification_sent"] = email_sent

                messages.success(
                    request,
                    f"Your account has been automatically approved! Please check your email ({user.email}) to verify your email address before signing in.",
                )
            else:
                # Update the user status and save again
                user.is_active = False  # User needs manual approval
                user.save()

                # Set session variables for success template
                request.session["registration_auto_approved"] = False
                request.session["registration_email"] = user.email
                request.session["email_verification_sent"] = email_sent

                messages.success(
                    request,
                    "Registration successful! Please check your email to verify your email address. Your account is also pending approval.",
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
    context = {
        "registration_auto_approved": request.session.get(
            "registration_auto_approved", False
        ),
        "registration_email": request.session.get("registration_email", ""),
        "email_verification_sent": request.session.get(
            "email_verification_sent", False
        ),
    }

    # Clear the session variables after displaying them
    if "registration_auto_approved" in request.session:
        del request.session["registration_auto_approved"]
    if "registration_email" in request.session:
        del request.session["registration_email"]
    if "email_verification_sent" in request.session:
        del request.session["email_verification_sent"]

    return render(request, "registration_success.html", context)


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


def verify_email(request, token):
    """Verify email address using the provided token"""
    try:
        user = get_object_or_404(User, email_verification_token=token)

        if user.is_email_verified:
            messages.info(request, "Your email address has already been verified.")
        else:
            user.verify_email()
            messages.success(
                request, "Email address verified successfully! You can now sign in."
            )

        return redirect("account")

    except User.DoesNotExist:
        messages.error(
            request,
            "Invalid verification link. Please contact support if you continue to have issues.",
        )
        return redirect("account")


def resend_verification_email(request):
    """Resend verification email for logged-in users or by email"""
    if request.user.is_authenticated:
        # Handle logged-in users
        if request.user.is_email_verified:
            messages.info(request, "Your email address is already verified.")
            return redirect("account")

        if request.method == "POST":
            email_sent = send_verification_email(request.user, request)
            if email_sent:
                messages.success(
                    request, f"Verification email sent to {request.user.email}."
                )
            else:
                messages.error(
                    request,
                    "Failed to send verification email. Please try again or contact support.",
                )
    else:
        # Handle unauthenticated users - they need to provide email
        if request.method == "POST":
            email = request.POST.get("email", "").strip()
            if not email:
                messages.error(request, "Please provide your email address.")
                return redirect("account")

            try:
                user = User.objects.get(email__iexact=email)
                if user.is_email_verified:
                    messages.info(request, "Your email address is already verified.")
                    return redirect("account")

                email_sent = send_verification_email(user, request)
                if email_sent:
                    messages.success(
                        request, f"Verification email sent to {user.email}."
                    )
                    # Show success message on the resend page
                    return render(
                        request,
                        "resend_verification.html",
                        {"email_sent": True, "user_email": user.email},
                    )
                else:
                    messages.error(
                        request,
                        "Failed to send verification email. Please try again or contact support.",
                    )
            except User.DoesNotExist:
                messages.error(request, "No account found with that email address.")

        # Show form for email input (GET request or after error)
        return render(request, "resend_verification.html")

    return redirect("account")

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
from .forms import UserRegistrationForm, UserProfileUpdateForm, PasswordResetForm
from .models import User
from .domain_management import should_auto_approve, get_email_domain
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import ensure_csrf_cookie


def send_verification_email(user, request):
    """Send email verification email to user"""
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart

    try:
        # Generate a new verification token
        user.generate_verification_token()

        # Build verification URL
        verification_url = request.build_absolute_uri(
            f"/users/verify-email/{user.email_verification_token}/"
        )

        # Build logo URL - use production domain for emails since localhost won't work
        # Email clients can't access localhost URLs
        is_localhost = (
            "localhost" in request.get_host() or "127.0.0.1" in request.get_host()
        )

        if is_localhost:
            # Use production domain so emails display properly
            logo_url = "https://member.bit.bio/static/images/bitbio-logo.png"
        else:
            # Use current domain
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
        except Exception as smtp_error:
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

        return True
    except smtplib.SMTPAuthenticationError as e:
        return False
    except smtplib.SMTPRecipientsRefused as e:
        return False
    except smtplib.SMTPServerDisconnected as e:
        return False
    except Exception as e:
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


def send_password_reset_email(user, request):
    """Send password reset email to user"""
    try:
        # Generate a new password reset token
        user.generate_password_reset_token()

        # Build reset URL
        reset_url = request.build_absolute_uri(
            f"/account/reset/{user.password_reset_token}/"
        )

        # Build logo URL - use production domain for emails since localhost won't work
        # Email clients can't access localhost URLs
        is_localhost = (
            "localhost" in request.get_host() or "127.0.0.1" in request.get_host()
        )

        if is_localhost:
            # Use production domain so emails display properly
            logo_url = "https://member.bit.bio/static/images/bitbio-logo.png"
        else:
            # Use current domain
            logo_url = request.build_absolute_uri("/static/images/bitbio-logo.png")

        # Prepare email context
        context = {
            "user": user,
            "reset_url": reset_url,
            "site_name": "Bit.bio",
            "logo_url": logo_url,
        }

        # Render email templates
        html_message = render_to_string("emails/password_reset.html", context)
        plain_message = render_to_string("emails/password_reset.txt", context)

        # Send email using Django's send_mail
        result = send_mail(
            subject="Customer account password reset",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )

        return True
    except Exception as e:
        return False


def password_reset_request(request):
    """Handle password reset request - checks Shopify instead of Django database"""
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please provide your email address.")
            return redirect("account")

        # Check if customer exists in Shopify
        shopify_customer = check_shopify_customer_exists(email)

        if shopify_customer:
            # Customer exists in Shopify
            # Create or get Django user
            user = create_django_user_from_shopify(shopify_customer)

            if user:
                # Send password reset email
                email_sent = send_password_reset_email(user, request)
                if email_sent:
                    messages.success(
                        request,
                        f"We've sent you an email with a link to update your password.",
                    )
                else:
                    messages.error(
                        request,
                        "Failed to send password reset email. Please try again or contact support.",
                    )
            else:
                messages.error(
                    request,
                    "Failed to process password reset request. Please contact support.",
                )
        else:
            # Customer doesn't exist in Shopify
            # Don't reveal if email exists or not for security reasons
            messages.success(
                request,
                "If an account with that email exists, password reset instructions have been sent.",
            )

    return redirect("account")


@ensure_csrf_cookie
def reset_password_with_token(request, token):
    """Handle password reset with token"""
    try:
        # Find user with the token
        user = User.objects.get(password_reset_token=token)

        # Check if token is not too old (24 hours)
        if user.password_reset_sent_at:
            from datetime import timedelta

            token_age = timezone.now() - user.password_reset_sent_at
            if token_age > timedelta(hours=24):
                user.password_reset_token = None
                user.password_reset_sent_at = None
                user.save()
                messages.error(
                    request,
                    "Password reset link has expired. Please request a new one.",
                )
                return render(request, "reset_password.html", {"token_valid": False})

        token_valid = True

    except User.DoesNotExist:
        token_valid = False
        messages.error(request, "Invalid password reset link.")
        return render(request, "reset_password.html", {"token_valid": False})

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            # Update password
            new_password = form.cleaned_data["password1"]
            user.set_password(new_password)

            # Clear the reset token
            user.password_reset_token = None
            user.password_reset_sent_at = None
            user.save()

            # Update password in Shopify if user has Shopify account
            shopify_update_success = False
            try:
                from .models import ShopifyUserSession

                shopify_session = ShopifyUserSession.objects.get(
                    shopify_email__iexact=user.email
                )

                # Update Shopify customer password
                shopify_update_success = update_shopify_customer_password(
                    shopify_session.shopify_customer_id, new_password
                )

            except ShopifyUserSession.DoesNotExist:
                # User doesn't have Shopify account, just update local password
                pass
            except Exception as e:
                # Shopify update failed, but local password was updated
                pass

            # Display appropriate success message based on Shopify update result
            try:
                from .models import ShopifyUserSession

                has_shopify = ShopifyUserSession.objects.filter(
                    shopify_email__iexact=user.email
                ).exists()

                if has_shopify:
                    if shopify_update_success:
                        messages.success(
                            request,
                            "Password updated successfully!",
                        )
                    else:
                        messages.warning(
                            request,
                            "Password updated successfully for your account. However, we couldn't sync it to your Shopify store. Please update your Shopify password separately if needed.",
                        )
                else:
                    messages.success(request, "Password updated successfully!")
            except Exception:
                messages.success(request, "Password updated successfully!")

            return redirect("account")
    else:
        form = PasswordResetForm()

    context = {
        "form": form,
        "token_valid": token_valid,
    }
    return render(request, "reset_password.html", context)


def check_shopify_customer_exists(email):
    """Check if a customer exists in Shopify by email"""
    import requests  # pyright: ignore[reportMissingModuleSource]
    from django.conf import settings

    try:
        # Get Shopify credentials from settings
        shopify_domain = getattr(settings, "SHOPIFY_DOMAIN", "bit-bio.myshopify.com")
        shopify_token = getattr(settings, "SHOPIFY_ACCESS_TOKEN", "")

        if not shopify_token:
            return None

        # Shopify API endpoint for searching customers by email
        url = f"https://{shopify_domain}/admin/api/2023-10/customers/search.json"

        headers = {
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json",
        }

        params = {"query": f"email:{email}"}

        response = requests.get(url, headers=headers, params=params)

        if response.status_code == 200:
            data = response.json()
            customers = data.get("customers", [])

            if customers:
                # Return the first matching customer
                customer = customers[0]
                return customer
            else:
                return None
        else:
            return None

    except Exception as e:
        return None


def update_shopify_customer_password(customer_id, new_password):
    """Update customer password in Shopify using REST API"""
    import requests  # pyright: ignore[reportMissingModuleSource]
    from django.conf import settings

    try:
        # Get Shopify credentials from settings
        shopify_domain = getattr(settings, "SHOPIFY_DOMAIN", "bit-bio.myshopify.com")
        shopify_token = getattr(settings, "SHOPIFY_ACCESS_TOKEN", "")

        if not shopify_token:
            return False

        # Shopify REST API endpoint for updating customer
        # Use the latest stable API version
        url = f"https://{shopify_domain}/admin/api/2024-01/customers/{customer_id}.json"

        headers = {
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json",
        }

        # Prepare the data for password update
        data = {
            "customer": {
                "id": customer_id,
                "password": new_password,
                "password_confirmation": new_password,
            }
        }

        response = requests.put(url, json=data, headers=headers)

        if response.status_code == 200:
            return True
        else:
            return False

    except Exception as e:
        return False


def create_django_user_from_shopify(shopify_customer):
    """Create or update Django user from Shopify customer data"""
    try:
        email = shopify_customer["email"]
        first_name = shopify_customer.get("first_name", "")
        last_name = shopify_customer.get("last_name", "")

        # Check if Django user already exists
        try:
            user = User.objects.get(email=email)
            return user
        except User.DoesNotExist:
            # Create new Django user
            user = User.objects.create_user(
                email=email,
                password="temp_password_123",  # Temporary password, will be reset
                first_name=first_name,
                last_name=last_name,
                job_title="Customer",  # Default job title
                is_active=True,
                is_email_verified=True,
                status="approved",
            )

            # Create or update ShopifyUserSession
            from .models import ShopifyUserSession

            shopify_session, created = ShopifyUserSession.objects.get_or_create(
                shopify_email=email,
                defaults={
                    "shopify_customer_id": shopify_customer["id"],
                    "shopify_first_name": first_name,
                    "shopify_last_name": last_name,
                    "shopify_verified_email": shopify_customer.get(
                        "verified_email", False
                    ),
                },
            )

            if not created:
                # Update existing session
                shopify_session.shopify_customer_id = shopify_customer["id"]
                shopify_session.shopify_first_name = first_name
                shopify_session.shopify_last_name = last_name
                shopify_session.shopify_verified_email = shopify_customer.get(
                    "verified_email", False
                )
                shopify_session.save()

            return user

    except Exception as e:
        return None

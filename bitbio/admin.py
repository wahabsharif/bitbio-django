# bitbio/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django import forms

from app_users.models import User as CustomUser, Domain
from app_users.admin_forms import EmailAuthenticationForm, DomainManagementForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from bitbio.countries import COUNTRIES


class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users in admin"""

    is_client = forms.BooleanField(
        required=False,
        label="Is Client",
        help_text="Check this if the user is a client",
        widget=forms.CheckboxInput(attrs={"id": "id_is_client"}),
    )
    is_staff = forms.BooleanField(
        required=False,
        label="Is Staff",
        help_text="Check this if the user is a staff member",
        widget=forms.CheckboxInput(attrs={"id": "id_is_staff"}),
    )

    # Billing information fields (same as registration form)
    company_trading_name = forms.CharField(
        max_length=200,
        required=False,
        label="Company Trading Name",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        label="Billing Address Line 1",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        label="Billing Address Line 2",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_city = forms.CharField(
        max_length=100,
        required=False,
        label="Billing City",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_postal_code = forms.CharField(
        max_length=20,
        required=False,
        label="Billing Postal Code",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_state = forms.CharField(
        max_length=100,
        required=False,
        label="Billing State",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    billing_country = forms.ChoiceField(
        choices=[("", "Select Country")]
        + [(country, country) for country in COUNTRIES],
        required=False,
        label="Billing Country",
        widget=forms.Select(attrs={"class": "vTextField"}),
    )
    billing_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Billing Phone",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )

    # Shipping information fields (same as registration form)
    shipping_address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        label="Shipping Address Line 1",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        label="Shipping Address Line 2",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_city = forms.CharField(
        max_length=100,
        required=False,
        label="Shipping City",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        required=False,
        label="Shipping Postal Code",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_state = forms.CharField(
        max_length=100,
        required=False,
        label="Shipping State",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_country = forms.ChoiceField(
        choices=[("", "Select Country")]
        + [(country, country) for country in COUNTRIES],
        required=False,
        label="Shipping Country",
        widget=forms.Select(attrs={"class": "vTextField"}),
    )
    shipping_phone = forms.CharField(
        max_length=20,
        required=False,
        label="Shipping Phone",
        widget=forms.TextInput(attrs={"class": "vTextField"}),
    )
    shipping_instructions = forms.CharField(
        required=False,
        label="Shipping Instructions",
        widget=forms.Textarea(attrs={"class": "vLargeTextField", "rows": 3}),
    )

    # Other fields
    institution_tax_vat = forms.BooleanField(
        required=False, label="Institution is Tax/VAT Exempt"
    )
    in_vitro = forms.BooleanField(
        required=False, label="Research use only (RUO): in vitro"
    )
    in_vivo = forms.BooleanField(
        required=False, label="Research use only (RUO): in vivo"
    )
    communications_agreement = forms.BooleanField(
        required=False, label="Agree to receive communications"
    )
    status = forms.ChoiceField(
        choices=[
            ("pending", "Pending"),
            ("approved", "Approved"),
            ("rejected", "Rejected"),
        ],
        initial="pending",
        required=False,
        label="Status",
    )
    is_active = forms.BooleanField(initial=True, required=False, label="Is Active")

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "job_title",
            "is_client",
            "is_staff",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make email required and set it as the username field
        self.fields["email"].required = True
        # Remove username field if it exists (since we use email)
        if "username" in self.fields:
            del self.fields["username"]

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with this email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.job_title = self.cleaned_data["job_title"]
        user.is_client = self.cleaned_data.get("is_client", False)
        user.is_staff = self.cleaned_data.get("is_staff", False)

        # Set billing information as JSON (same as registration form)
        billing_info = {
            "company_trading_name": self.cleaned_data.get("company_trading_name", ""),
            "address_line_1": self.cleaned_data.get("billing_address_line_1", ""),
            "address_line_2": self.cleaned_data.get("billing_address_line_2", ""),
            "city": self.cleaned_data.get("billing_city", ""),
            "postal_code": self.cleaned_data.get("billing_postal_code", ""),
            "state": self.cleaned_data.get("billing_state", ""),
            "country": self.cleaned_data.get("billing_country", ""),
            "phone_number": self.cleaned_data.get("billing_phone", ""),
        }
        user.billing_information = billing_info

        # Set shipping information as JSON (same as registration form)
        shipping_info = {
            "address_line_1": self.cleaned_data.get("shipping_address_line_1", ""),
            "address_line_2": self.cleaned_data.get("shipping_address_line_2", ""),
            "city": self.cleaned_data.get("shipping_city", ""),
            "postal_code": self.cleaned_data.get("shipping_postal_code", ""),
            "state": self.cleaned_data.get("shipping_state", ""),
            "country": self.cleaned_data.get("shipping_country", ""),
            "phone_number": self.cleaned_data.get("shipping_phone", ""),
            "instructions": self.cleaned_data.get("shipping_instructions", ""),
        }
        user.shipping_information = shipping_info

        user.institution_tax_vat = self.cleaned_data.get("institution_tax_vat", False)
        user.in_vitro = self.cleaned_data.get("in_vitro", False)
        user.in_vivo = self.cleaned_data.get("in_vivo", False)
        user.communications_agreement = self.cleaned_data.get(
            "communications_agreement", False
        )
        user.status = self.cleaned_data.get("status", "pending")
        user.is_active = self.cleaned_data.get("is_active", True)

        if commit:
            user.save()
        return user


class BitBioAdminSite(AdminSite):
    site_header = "🧬 BitBio Administration"
    site_title = "BitBio Admin Portal"
    index_title = "Welcome to BitBio Administration"
    site_url = "/"

    # Use custom login form
    login_form = EmailAuthenticationForm

    # Override the index template
    index_template = "admin/index.html"

    def has_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        the admin site. Only superusers and staff members can access.
        """
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )

    def login(self, request, extra_context=None):
        """
        Custom login view with enhanced security checks.
        """
        # If user is already authenticated and has admin access, redirect to admin index
        if request.user.is_authenticated:
            if request.user.is_active and (
                request.user.is_staff or request.user.is_superuser
            ):
                # User has admin access, redirect to admin index
                from django.shortcuts import redirect

                return redirect("/admin/")
            else:
                # User is logged in but doesn't have admin access
                # Instead of redirecting to home page (which causes loops),
                # log them out and show the login form
                from django.contrib.auth import logout
                from django.contrib import messages

                logout(request)
                messages.warning(
                    request,
                    "You were logged out because you don't have admin access. Please log in with an admin account.",
                )

        return super().login(request, extra_context)

    def logout(self, request, extra_context=None):
        """
        Custom logout view that redirects to main login page instead of showing logout page.
        """
        from django.contrib.auth import logout
        from django.shortcuts import redirect

        logout(request)
        # Redirect to main login page instead of showing Django's logout page
        return redirect("/admin")

    def has_module_permission(self, request):
        """
        Return True if the given HttpRequest has permission to view
        the module index page. Only superusers and staff members can access.
        """
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )

    def get_urls(self):
        urls = super().get_urls()
        # Remove the custom dashboard URL to avoid conflicts
        # The index template will handle the dashboard display
        return urls

    def each_context(self, request):
        """Add common context to all admin views"""
        context = super().each_context(request)
        try:
            context.update(
                {
                    "user_count": CustomUser.objects.count(),
                    "pending_count": CustomUser.objects.filter(
                        status="pending"
                    ).count(),
                    "approved_count": CustomUser.objects.filter(
                        status="approved"
                    ).count(),
                    "rejected_count": CustomUser.objects.filter(
                        status="rejected"
                    ).count(),
                    "recent_users": CustomUser.objects.order_by("-created_at")[:5],
                    "domain_count": Domain.objects.count(),
                    "whitelisted_domains_count": sum(
                        len(obj.whitelisted_domains or [])
                        for obj in Domain.objects.all()
                    ),
                    "blocklisted_domains_count": sum(
                        len(obj.blocklisted_domains or [])
                        for obj in Domain.objects.all()
                    ),
                    "domain_management_url": (
                        reverse(
                            "admin:app_users_domain_change",
                            args=[Domain.objects.first().id],
                        )
                        if Domain.objects.exists()
                        else None
                    ),
                }
            )
        except Exception as e:
            # Fallback if there are any database issues
            context.update(
                {
                    "user_count": 0,
                    "pending_count": 0,
                    "approved_count": 0,
                    "rejected_count": 0,
                    "recent_users": [],
                    "domain_count": 0,
                    "whitelisted_domains_count": 0,
                    "blocklisted_domains_count": 0,
                }
            )
        return context


# Create custom admin site instance
admin_site = BitBioAdminSite(name="admin")


# Register models with custom admin site
@admin.register(CustomUser, site=admin_site)
class CustomUserAdmin(admin.ModelAdmin):
    change_list_template = "admin/app_users/user/change_list.html"
    change_form_template = "admin/app_users/user/change_form.html"
    list_display = (
        "email",
        "first_name",
        "last_name",
        "job_title",
        "status_badge",
        "is_superuser",
        "is_active",
        "is_staff",
        "is_client",
        "last_login",
        "institution_tax_vat",
        "in_vitro",
        "in_vivo",
        "communications_agreement",
        "date_joined",
        "billing_info_display",
        "shipping_info_display",
        "is_email_verified",
        "email_verification_sent_at",
        "email_verification_token",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "institution_tax_vat",
        "in_vitro",
        "in_vivo",
        "communications_agreement",
        "is_active",
        "is_staff",
        "is_client",
        "is_superuser",
        "created_at",
        "date_joined",
    )
    search_fields = ("email", "first_name", "last_name", "job_title")
    ordering = ("-created_at",)
    list_per_page = 25

    actions = ["approve_users", "reject_users", "apply_queued_changes"]

    fieldsets = (
        (None, {"fields": ("email",)}),
        ("Personal info", {"fields": ("first_name", "last_name", "job_title")}),
        (
            "Billing Information",
            {"fields": ("billing_information", "institution_tax_vat")},
        ),
        ("Shipping Information", {"fields": ("shipping_information",)}),
        ("Use Intent", {"fields": ("in_vitro", "in_vivo")}),
        ("Consent", {"fields": ("communications_agreement",)}),
        (
            "Status",
            {
                "fields": (
                    "status",
                    "is_active",
                    "is_staff",
                    "is_client",
                    "is_superuser",
                )
            },
        ),
        (
            "Important dates",
            {"fields": ("last_login", "date_joined", "created_at", "updated_at")},
        ),
        ("Permissions", {"fields": ("groups", "user_permissions")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "first_name",
                    "last_name",
                    "job_title",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")

    def get_readonly_fields(self, request, obj=None):
        """
        Make superuser fields read-only for non-superusers.
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))

        # If the current user is not a superuser, make superuser fields read-only
        if not request.user.is_superuser:
            readonly_fields.extend(["is_superuser", "is_staff", "is_client"])

        return readonly_fields

    def has_add_permission(self, request):
        """
        Only superusers can add new users.
        """
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        """
        Only superusers can delete users.
        """
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        """
        Only superusers and staff can change users.
        """
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )

    def has_view_permission(self, request, obj=None):
        """
        Only superusers and staff can view users.
        """
        return request.user.is_active and (
            request.user.is_staff or request.user.is_superuser
        )

    # Override get_form to handle password fields properly
    def get_form(self, request, obj=None, **kwargs):
        if obj is None:  # Adding new user
            return CustomUserCreationForm

        # Use a custom form for editing existing users
        form_class = super().get_form(request, obj, **kwargs)

        class CustomUserChangeForm(form_class):
            def save(self, commit=True):
                # Get original status before saving
                original_status = None
                if self.instance.pk:
                    try:
                        original_user = CustomUser.objects.get(pk=self.instance.pk)
                        original_status = original_user.status
                    except CustomUser.DoesNotExist:
                        pass

                # Save the user
                user = super().save(commit)

                # Check if status changed from pending to approved
                if (
                    original_status == "pending"
                    and user.status == "approved"
                    and commit
                ):
                    # Send verification email
                    from app_users.views import send_verification_email
                    from django.test import RequestFactory

                    # Create a mock request for email sending
                    factory = RequestFactory()
                    request = factory.get("/admin/")
                    request.META["HTTP_HOST"] = "localhost:8000"
                    request.META["SERVER_PORT"] = "8000"
                    request.META["wsgi.url_scheme"] = "http"

                    try:
                        send_verification_email(user, request)
                    except Exception as e:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.error(
                            f"Failed to send verification email to {user.email}: {e}"
                        )

                return user

        return CustomUserChangeForm

    def get_fieldsets(self, request, obj=None):
        """
        Return different fieldsets for add vs. change operations.
        """
        if obj is None:  # Adding new user
            # For new users, show organized fieldsets with checkboxes and conditional fields
            return (
                (
                    "Personal Information",
                    {
                        "fields": (
                            "first_name",
                            "last_name",
                            "job_title",
                        )
                    },
                ),
                (
                    "Login Information",
                    {
                        "fields": (
                            "email",
                            "password1",
                            "password2",
                        )
                    },
                ),
                (
                    "User Type",
                    {
                        "fields": (
                            "is_client",
                            "is_staff",
                        ),
                        "classes": ("wide",),
                    },
                ),
                (
                    "Billing Information",
                    {
                        "fields": (
                            "company_trading_name",
                            "billing_address_line_1",
                            "billing_address_line_2",
                            "billing_city",
                            "billing_postal_code",
                            "billing_state",
                            "billing_country",
                            "billing_phone",
                            "institution_tax_vat",
                        ),
                        "classes": ("client-fieldset", "collapse"),
                        "description": "These fields are shown when 'Is Client' is checked.",
                    },
                ),
                (
                    "Shipping Information",
                    {
                        "fields": (
                            "shipping_address_line_1",
                            "shipping_address_line_2",
                            "shipping_city",
                            "shipping_postal_code",
                            "shipping_state",
                            "shipping_country",
                            "shipping_phone",
                            "shipping_instructions",
                        ),
                        "classes": ("client-fieldset", "collapse"),
                    },
                ),
                (
                    "Use Intent",
                    {
                        "fields": (
                            "in_vitro",
                            "in_vivo",
                        ),
                        "classes": ("client-fieldset", "collapse"),
                    },
                ),
                (
                    "Consent & Status",
                    {
                        "fields": (
                            "communications_agreement",
                            "status",
                            "is_active",
                        ),
                        "classes": ("client-fieldset", "collapse"),
                    },
                ),
            )
        else:
            # For existing users, show all fields
            return self.fieldsets

    def status_badge(self, obj):
        if obj.status == "approved":
            return format_html(
                '<span style="background: #27ae60; color: white; padding: 0.25rem 0.75rem; font-size: 0.8rem;">✓ Approved</span>'
            )
        elif obj.status == "pending":
            return format_html(
                '<span style="background: #f39c12; color: white; padding: 0.25rem 0.75rem; font-size: 0.8rem;">⏳ Pending</span>'
            )
        else:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 0.25rem 0.75rem; font-size: 0.8rem;">✗ Rejected</span>'
            )

    status_badge.short_description = "Status"

    def billing_info_display(self, obj):
        """Display billing information in a readable format"""
        if obj.billing_information:
            info = obj.get_billing_info()
            if info:
                # Show key billing details with proper formatting
                display_parts = []
                if info.get("company_trading_name"):
                    display_parts.append(
                        f"<strong>Company:</strong> {info['company_trading_name']}"
                    )
                if info.get("address_line_1"):
                    display_parts.append(
                        f"<strong>Address:</strong> {info['address_line_1']}"
                    )
                if info.get("city"):
                    display_parts.append(f"<strong>City:</strong> {info['city']}")
                if info.get("country"):
                    display_parts.append(f"<strong>Country:</strong> {info['country']}")
                if info.get("postal_code"):
                    display_parts.append(
                        f"<strong>Postal Code:</strong> {info['postal_code']}"
                    )
                if info.get("phone_number"):
                    display_parts.append(
                        f"<strong>Phone:</strong> {info['phone_number']}"
                    )

                if display_parts:
                    return format_html(
                        '<div style="max-width: 200px; word-wrap: break-word;">'
                        + "<br>".join(display_parts)
                        + "</div>"
                    )
                else:
                    return format_html(
                        '<span style="color: #666; font-style: italic;">Billing info available</span>'
                    )
            else:
                return format_html(
                    '<span style="color: #666; font-style: italic;">No billing info</span>'
                )
        return format_html(
            '<span style="color: #666; font-style: italic;">No billing info</span>'
        )

    billing_info_display.short_description = "Billing Information"

    def shipping_info_display(self, obj):
        """Display shipping information in a readable format"""
        if obj.shipping_information:
            info = obj.get_shipping_info()
            if info:
                # Show key shipping details with proper formatting
                display_parts = []
                if info.get("address_line_1"):
                    display_parts.append(
                        f"<strong>Address:</strong> {info['address_line_1']}"
                    )
                if info.get("city"):
                    display_parts.append(f"<strong>City:</strong> {info['city']}")
                if info.get("country"):
                    display_parts.append(f"<strong>Country:</strong> {info['country']}")
                if info.get("postal_code"):
                    display_parts.append(
                        f"<strong>Postal Code:</strong> {info['postal_code']}"
                    )
                if info.get("phone_number"):
                    display_parts.append(
                        f"<strong>Phone:</strong> {info['phone_number']}"
                    )

                if display_parts:
                    return format_html(
                        '<div style="max-width: 200px; word-wrap: break-word;">'
                        + "<br>".join(display_parts)
                        + "</div>"
                    )
                else:
                    return format_html(
                        '<span style="color: #666; font-style: italic;">Shipping info available</span>'
                    )
            else:
                return format_html(
                    '<span style="color: #666; font-style: italic;">No shipping info</span>'
                )
        return format_html(
            '<span style="color: #666; font-style: italic;">No shipping info</span>'
        )

    shipping_info_display.short_description = "Shipping Information"

    # Custom admin actions
    def approve_users(self, request, queryset):
        """Approve selected users"""
        from app_users.views import send_verification_email
        import logging

        logger = logging.getLogger(__name__)
        email_success_count = 0
        email_fail_count = 0

        # Get users that are currently pending before updating
        pending_users = list(queryset.filter(status="pending"))

        # Update both status and is_active for approved users
        updated = queryset.update(status="approved", is_active=True)

        # Send verification emails to users who were pending
        for user in pending_users:
            try:
                # Refresh the user object to get the updated status
                user.refresh_from_db()

                email_sent = send_verification_email(user, request)
                if email_sent:
                    email_success_count += 1
                else:
                    email_fail_count += 1
            except Exception as e:
                email_fail_count += 1
                logger.error(f"Failed to send verification email to {user.email}: {e}")

        # Create success message
        if updated == 1:
            message = "1 user was successfully approved and activated."
        else:
            message = f"{updated} users were successfully approved and activated."

        # Add email status to message
        if email_success_count > 0:
            message += f" Verification emails sent to {email_success_count} user(s)."
        if email_fail_count > 0:
            message += (
                f" Failed to send verification emails to {email_fail_count} user(s)."
            )

        self.message_user(request, message, messages.SUCCESS)

    approve_users.short_description = "Approve selected users"

    def reject_users(self, request, queryset):
        """Reject selected users"""
        updated = queryset.update(status="rejected")
        if updated == 1:
            message = "1 user was successfully rejected."
        else:
            message = f"{updated} users were successfully rejected."
        self.message_user(request, message, messages.SUCCESS)

    reject_users.short_description = "Reject selected users"

    def apply_queued_changes(self, request, queryset):
        """Apply queued status changes"""
        from app_users.views import send_verification_email
        import logging
        import json

        logger = logging.getLogger(__name__)
        applied_count = 0
        email_count = 0

        # Get changes from POST data
        changes_data = []
        for key, value in request.POST.items():
            if key.startswith("changes[") and key.endswith("].userId"):
                index = key.split("[")[1].split("]")[0]
                changes_data.append(
                    {
                        "userId": value,
                        "fromStatus": request.POST.get(
                            f"changes[{index}].fromStatus", ""
                        ),
                        "toStatus": request.POST.get(f"changes[{index}].toStatus", ""),
                    }
                )

        # Apply each change
        for change in changes_data:
            try:
                user = CustomUser.objects.get(pk=change["userId"])
                original_status = user.status

                # Send verification email if status changed from pending to approved
                if original_status == "pending" and change["toStatus"] == "approved":
                    try:
                        from django.test import RequestFactory
                        from django.conf import settings

                        factory = RequestFactory()
                        mock_request = factory.get("/admin/")

                        # Use settings to determine the correct host and scheme
                        if (
                            hasattr(settings, "ALLOWED_HOSTS")
                            and settings.ALLOWED_HOSTS
                        ):
                            host = settings.ALLOWED_HOSTS[0]
                        else:
                            host = "localhost:8000"

                        mock_request.META["HTTP_HOST"] = host
                        mock_request.META["SERVER_PORT"] = "8000"
                        mock_request.META["wsgi.url_scheme"] = "http"

                        # Add user to the request for proper context
                        mock_request.user = request.user

                        email_sent = send_verification_email(user, mock_request)
                        if email_sent:
                            email_count += 1
                            logger.info(
                                f"Verification email sent to {user.email} via modal update"
                            )
                        else:
                            logger.warning(
                                f"Failed to send verification email to {user.email} via modal update"
                            )
                    except Exception as e:
                        logger.error(
                            f"Failed to send verification email to {user.email}: {e}"
                        )

                # Update status
                user.status = change["toStatus"]
                if change["toStatus"] == "approved":
                    user.is_active = True
                user.save()

                applied_count += 1

            except CustomUser.DoesNotExist:
                logger.error(f"User with ID {change['userId']} not found")
            except Exception as e:
                logger.error(f"Error applying change for user {change['userId']}: {e}")

        # Return JSON response for AJAX requests
        if request.headers.get(
            "X-Requested-With"
        ) == "XMLHttpRequest" or "application/json" in request.headers.get(
            "Accept", ""
        ):
            from django.http import JsonResponse

            # Create success message
            if applied_count == 1:
                message = f"1 change applied successfully. {email_count} verification emails sent."
            else:
                message = f"{applied_count} changes applied successfully. {email_count} verification emails sent."

            return JsonResponse(
                {
                    "success": True,
                    "applied_count": applied_count,
                    "email_count": email_count,
                    "message": message,
                }
            )

        # Regular admin response
        if applied_count == 1:
            message = f"1 change applied successfully. {email_count} verification emails sent."
        else:
            message = f"{applied_count} changes applied successfully. {email_count} verification emails sent."

        self.message_user(request, message, messages.SUCCESS)

    apply_queued_changes.short_description = "Apply queued changes"

    def changelist_view(self, request, extra_context=None):
        """Override changelist_view to handle queued changes POST request"""
        if (
            request.method == "POST"
            and request.POST.get("action") == "apply_queued_changes"
        ):
            # Handle the queued changes application
            return self.apply_queued_changes(request, self.get_queryset(request))

        return super().changelist_view(request, extra_context)

    def get_queryset(self, request):
        """Exclude the currently logged-in user from the queryset"""
        queryset = super().get_queryset(request).select_related()
        # Exclude the currently logged-in user from the list
        return queryset.exclude(id=request.user.id)

    def save_model(self, request, obj, form, change):
        if change:  # Existing user being updated
            # Check if status is being changed to approved
            if obj.status == "approved":
                obj.is_active = True
        elif not change:  # New user
            # Password is already handled by UserCreationForm
            pass
        super().save_model(request, obj, form, change)


# Register Domain model with custom admin site
@admin.register(Domain, site=admin_site)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for Domain model
    """

    form = DomainManagementForm

    list_display = (
        "whitelisted_count",
        "blocklisted_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    readonly_fields = ()

    # Disable adding new records - only allow editing existing ones
    def has_add_permission(self, request):
        """Disable adding new domain records"""
        return False

    # Disable deleting records
    def has_delete_permission(self, request, obj=None):
        """Disable deleting domain records"""
        return False

    # Change the list view to show edit link directly
    def changelist_view(self, request, extra_context=None):
        """Override changelist to redirect to edit the first domain record"""
        from django.shortcuts import redirect
        from django.urls import reverse

        # Get the first domain record
        domain_obj = Domain.objects.first()
        if domain_obj:
            # Redirect to edit the existing record
            return redirect(
                reverse("admin:app_users_domain_change", args=[domain_obj.id])
            )
        else:
            # If no record exists, create one and redirect to edit
            domain_obj = Domain.objects.create(
                whitelisted_domains=[], blocklisted_domains=[]
            )
            return redirect(
                reverse("admin:app_users_domain_change", args=[domain_obj.id])
            )

    def whitelisted_count(self, obj):
        """Display count of whitelisted domains"""
        return len(obj.whitelisted_domains) if obj.whitelisted_domains else 0

    whitelisted_count.short_description = "Whitelisted Domains"

    def blocklisted_count(self, obj):
        """Display count of blocklisted domains"""
        return len(obj.blocklisted_domains) if obj.blocklisted_domains else 0

    blocklisted_count.short_description = "Blocklisted Domains"

    fieldsets = (
        (
            "Domain Management",
            {
                "fields": ("whitelisted_domains_input", "blocklisted_domains_input"),
                "description": "Enter one domain per line. Empty lines will be ignored.",
            },
        ),
    )

    # Hide the original JSON fields from the form
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form:
            # Set the model dynamically
            form.Meta.model = Domain
            form.Meta.fields = [
                "whitelisted_domains_input",
                "blocklisted_domains_input",
            ]
        return form

    def save_model(self, request, obj, form, change):
        """Override save_model to create detailed change messages"""
        if change and hasattr(form, "get_domain_changes"):
            changes = form.get_domain_changes()

            # Create detailed change message
            change_messages = []

            if changes.get("whitelisted_added"):
                domains = ", ".join(changes["whitelisted_added"])
                change_messages.append(f"Added to whitelist: {domains}")

            if changes.get("whitelisted_removed"):
                domains = ", ".join(changes["whitelisted_removed"])
                change_messages.append(f"Removed from whitelist: {domains}")

            if changes.get("blocklisted_added"):
                domains = ", ".join(changes["blocklisted_added"])
                change_messages.append(f"Added to blocklist: {domains}")

            if changes.get("blocklisted_removed"):
                domains = ", ".join(changes["blocklisted_removed"])
                change_messages.append(f"Removed from blocklist: {domains}")

            if change_messages:
                # Store the detailed message for the history view
                obj._change_message = "; ".join(change_messages)

        super().save_model(request, obj, form, change)

    def construct_change_message(self, request, form, formsets, add=False):
        """Override to provide custom change messages"""
        if add:
            return "Domain management record created."

        if hasattr(form, "get_domain_changes"):
            changes = form.get_domain_changes()

            # Create detailed change message
            change_messages = []

            if changes.get("whitelisted_added"):
                domains = ", ".join(changes["whitelisted_added"])
                change_messages.append(f"Added to whitelist: {domains}")

            if changes.get("whitelisted_removed"):
                domains = ", ".join(changes["whitelisted_removed"])
                change_messages.append(f"Removed from whitelist: {domains}")

            if changes.get("blocklisted_added"):
                domains = ", ".join(changes["blocklisted_added"])
                change_messages.append(f"Added to blocklist: {domains}")

            if changes.get("blocklisted_removed"):
                domains = ", ".join(changes["blocklisted_removed"])
                change_messages.append(f"Removed from blocklist: {domains}")

            if change_messages:
                return "; ".join(change_messages)

        return "Domain lists updated."


# Override the default admin site
admin.site = admin_site

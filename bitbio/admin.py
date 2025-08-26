# bitbio/admin.py

from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.contrib.auth.forms import UserCreationForm
from django import forms

from app_users.models import User as CustomUser
from app_users.admin_forms import EmailAuthenticationForm
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class CustomUserCreationForm(UserCreationForm):
    """Custom form for creating users in admin"""

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "first_name", "last_name", "job_title")

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
                }
            )
        return context


# Create custom admin site instance
admin_site = BitBioAdminSite(name="bitbio_admin")


# Register models with custom admin site
@admin.register(CustomUser, site=admin_site)
class CustomUserAdmin(admin.ModelAdmin):
    change_list_template = "admin/change_list.html"
    list_display = (
        "email",
        "first_name",
        "last_name",
        "job_title",
        "institution_tax_vat",
        "in_vitro",
        "in_vivo",
        "communications_agreement",
        "status",
        "is_active",
        "is_staff",
        "is_client",
        "is_superuser",
        "last_login",
        "date_joined",
        "created_at",
        "updated_at",
        "status_badge",
        "billing_info_display",
        "shipping_info_display",
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

    actions = ["approve_users", "reject_users"]

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
        return super().get_form(request, obj, **kwargs)

    def get_fieldsets(self, request, obj=None):
        """
        Return different fieldsets for add vs. change operations.
        """
        if obj is None:  # Adding new user
            # For new users, only show the fields available in CustomUserCreationForm
            return (
                (
                    None,
                    {
                        "fields": (
                            "first_name",
                            "last_name",
                            "job_title",
                            "email",
                            "password1",
                            "password2",
                        )
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
        updated = queryset.update(status="approved")
        if updated == 1:
            message = "1 user was successfully approved."
        else:
            message = f"{updated} users were successfully approved."
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()

    def save_model(self, request, obj, form, change):
        if not change:  # New user
            # Password is already handled by UserCreationForm
            pass
        super().save_model(request, obj, form, change)


# Override the default admin site
admin.site = admin_site

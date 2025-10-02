from django.contrib import admin
from .models import User, Domain, ShopifyUserSession


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    """
    Admin interface for Domain model
    """

    list_display = (
        "id",
        "whitelisted_count",
        "blocklisted_count",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")

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
            "Domain Lists",
            {
                "fields": ("whitelisted_domains", "blocklisted_domains"),
                "description": 'Enter domains as a JSON list. Example: ["stanford.edu", "harvard.edu"]',
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin interface for User model
    """

    list_display = (
        "email",
        "first_name",
        "last_name",
        "job_title",
        "status",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "status",
        "is_active",
        "is_staff",
        "is_client",
        "date_joined",
        "created_at",
    )
    search_fields = ("email", "first_name", "last_name", "job_title")
    readonly_fields = ("created_at", "updated_at", "date_joined")

    fieldsets = (
        (
            "Basic Information",
            {"fields": ("first_name", "last_name", "email", "job_title")},
        ),
        (
            "Status & Permissions",
            {"fields": ("status", "is_active", "is_staff", "is_client")},
        ),
        (
            "Billing & Shipping",
            {
                "fields": (
                    "billing_information",
                    "shipping_information",
                    "institution_tax_vat",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Use Intent",
            {
                "fields": ("in_vitro", "in_vivo", "communications_agreement"),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("date_joined", "created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ShopifyUserSession)
class ShopifyUserSessionAdmin(admin.ModelAdmin):
    """
    Admin interface for ShopifyUserSession model
    """

    list_display = (
        "shopify_customer_id",
        "shopify_email",
        "shopify_verified_email",
        "last_sync_at",
        "created_at",
    )
    list_filter = (
        "shopify_verified_email",
        "created_at",
        "last_sync_at",
    )
    search_fields = (
        "shopify_email",
        "shopify_customer_id",
        "shopify_first_name",
        "shopify_last_name",
    )
    readonly_fields = ("created_at", "last_sync_at")

    fieldsets = (
        (
            "Shopify Customer Data",
            {
                "fields": (
                    "shopify_customer_id",
                    "shopify_access_token",
                    "shopify_email",
                    "shopify_first_name",
                    "shopify_last_name",
                    "shopify_verified_email",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "last_sync_at"),
                "classes": ("collapse",),
            },
        ),
    )

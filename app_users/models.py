from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.validators import EmailValidator
from django.utils import timezone
import json
import uuid


class UserManager(BaseUserManager):
    """
    Custom user manager that creates users with email for authentication.
    """

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("status", "approved")
        extra_fields.setdefault("is_email_verified", True)  # Auto-verify admin emails

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Basic user information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    job_title = models.CharField(max_length=200)

    # Billing information as JSON
    billing_information = models.JSONField(default=dict, blank=True)

    # Institution tax/VAT exemption
    institution_tax_vat = models.BooleanField(default=False)

    # Client status
    is_client = models.BooleanField(default=False)

    # Shipping information as JSON
    shipping_information = models.JSONField(default=dict, blank=True)

    # Use intent
    in_vitro = models.BooleanField(default=False)
    in_vivo = models.BooleanField(default=False)

    # Communications agreement
    communications_agreement = models.BooleanField(default=False)

    # Approval status
    APPROVAL_CHOICES = [
        ("pending", "Pending"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
    ]
    status = models.CharField(
        max_length=20, choices=APPROVAL_CHOICES, default="pending", db_index=True
    )

    # Email verification fields
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(
        null=True, blank=True, unique=True, db_index=True
    )
    email_verification_sent_at = models.DateTimeField(null=True, blank=True)

    # Django auth fields
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True, db_index=True)
    date_joined = models.DateTimeField(default=timezone.now)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Use email as the primary identifier for authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "job_title"]

    # Use custom user manager
    objects = UserManager()

    class Meta:
        db_table = "app_users"
        verbose_name = "User"
        indexes = [
            models.Index(fields=["status", "is_active"], name="user_status_active_idx"),
            models.Index(
                fields=["email_verification_token"], name="user_verification_token_idx"
            ),
            models.Index(fields=["created_at"], name="user_created_at_idx"),
        ]
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def get_billing_info(self):
        """Get billing information as a dictionary"""
        if isinstance(self.billing_information, str):
            try:
                return json.loads(self.billing_information)
            except json.JSONDecodeError:
                return {}
        return self.billing_information or {}

    def get_shipping_info(self):
        """Get shipping information from a dictionary"""
        if isinstance(self.shipping_information, str):
            try:
                return json.loads(self.shipping_information)
            except json.JSONDecodeError:
                return {}
        return self.shipping_information or {}

    def set_billing_info(self, data):
        """Set billing information from a dictionary"""
        self.billing_information = data

    def set_shipping_info(self, data):
        """Set shipping information from a dictionary"""
        self.shipping_information = data

    @property
    def is_approved(self):
        """Check if user is approved"""
        return self.status == "approved"

    @property
    def is_pending(self):
        """Check if user is pending approval"""
        return self.status == "pending"

    @property
    def is_rejected(self):
        """Check if user is rejected"""
        return self.status == "rejected"

    def generate_verification_token(self):
        """Generate a new email verification token"""
        # Generate a unique token
        while True:
            new_token = uuid.uuid4()
            if not User.objects.filter(email_verification_token=new_token).exists():
                break

        self.email_verification_token = new_token
        self.email_verification_sent_at = timezone.now()
        self.save(
            update_fields=["email_verification_token", "email_verification_sent_at"]
        )

    def verify_email(self):
        """Mark email as verified"""
        self.is_email_verified = True
        self.save(update_fields=["is_email_verified"])

    @property
    def can_login(self):
        """Check if user can login (email verified and active)"""
        return self.is_email_verified and self.is_active


class Domain(models.Model):
    """
    Model to store domain management data including whitelisted and blocklisted domains
    """

    whitelisted_domains = models.JSONField(
        default=list,
        blank=True,
        help_text="List of whitelisted domains for auto-approval",
    )
    blocklisted_domains = models.JSONField(
        default=list,
        blank=True,
        help_text="List of blocklisted domains that are rejected",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "domains"
        verbose_name = "Domain"
        verbose_name_plural = "Domains"

    def __str__(self):
        return f"Domain Management ({len(self.whitelisted_domains or [])} whitelisted, {len(self.blocklisted_domains or [])} blocklisted)"

    @classmethod
    def get_or_create_domain_management(cls):
        """
        Get or create the main domain management record
        """
        # Since we only need one record, get the first one or create it
        domain_obj = cls.objects.first()
        if not domain_obj:
            domain_obj = cls.objects.create(
                whitelisted_domains=[], blocklisted_domains=[]
            )
        return domain_obj


class ShopifyUserSession(models.Model):
    """
    Model to store Shopify-specific user session data and customer information.
    This is now independent and does not require a User record.
    """

    # Shopify customer information
    shopify_customer_id = models.BigIntegerField(unique=True, db_index=True)
    shopify_access_token = models.TextField(null=True, blank=True)

    # Shopify customer data cache (email is now unique identifier)
    shopify_first_name = models.CharField(max_length=100, blank=True)
    shopify_last_name = models.CharField(max_length=100, blank=True)
    shopify_email = models.EmailField(unique=True, db_index=True)
    shopify_verified_email = models.BooleanField(default=False)

    # Session tracking
    last_sync_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "shopify_user_session"
        verbose_name = "Shopify User Session"
        verbose_name_plural = "Shopify User Sessions"
        indexes = [
            models.Index(
                fields=["shopify_customer_id"], name="shopify_customer_id_idx"
            ),
            models.Index(fields=["last_sync_at"], name="shopify_last_sync_idx"),
            models.Index(fields=["shopify_email"], name="shopify_email_idx"),
        ]

    def __str__(self):
        return f"Shopify Session for {self.shopify_email} (Customer ID: {self.shopify_customer_id})"

    @property
    def is_shopify_user(self):
        """Check if this user has a valid Shopify customer ID"""
        return self.shopify_customer_id is not None

    def update_shopify_data(self, customer_data):
        """Update Shopify customer data from API response"""
        self.shopify_first_name = customer_data.get("first_name", "")
        self.shopify_last_name = customer_data.get("last_name", "")
        self.shopify_email = customer_data.get("email", "")
        self.shopify_verified_email = customer_data.get("verified_email", False)
        self.save()

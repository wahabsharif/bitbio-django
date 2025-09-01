from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class EmailAuthenticationForm(AuthenticationForm):
    """
    Custom authentication form that uses email instead of username
    """

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(
            attrs={
                "class": "vTextField",
                "placeholder": "Enter your email address",
                "autocomplete": "email",
            }
        ),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "class": "vTextField",
                "placeholder": "Enter your password",
                "autocomplete": "current-password",
            }
        ),
    )

    def clean(self):
        email = self.cleaned_data.get("username")
        password = self.cleaned_data.get("password")

        if email and password:
            # Try to authenticate with email
            user = authenticate(username=email, password=password)
            if user is None:
                # Add error to the email field instead of general form error
                self.add_error(
                    "username",
                    _(
                        "Please enter a correct email and password. Note that both fields may be case-sensitive."
                    ),
                )
            elif not user.is_active:
                # Add error to the email field
                self.add_error("username", _("This account is inactive."))
            elif not (user.is_staff or user.is_superuser):
                # Add error to the email field
                self.add_error(
                    "username", _("You don't have permission to access the admin site.")
                )
            else:
                self.user_cache = user
        return self.cleaned_data


class DomainManagementForm(forms.ModelForm):
    """
    Custom form for Domain model that displays domains as individual input fields
    """

    # Custom fields for domain management
    whitelisted_domains_input = forms.CharField(
        label="Whitelisted Domains",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "vLargeTextField",
                "rows": 18,
                "placeholder": "Enter one domain per line\nExample:\nstanford.edu\nharvard.edu\nmit.edu",
                "help_text": "Enter one domain per line. These domains will be automatically approved.",
            }
        ),
        help_text="Enter one domain per line. These domains will be automatically approved.",
    )

    blocklisted_domains_input = forms.CharField(
        label="Blocklisted Domains",
        required=False,
        widget=forms.Textarea(
            attrs={
                "class": "vLargeTextField",
                "rows": 18,
                "placeholder": "Enter one domain per line\nExample:\ngmail.com\nyahoo.com\nhotmail.com",
                "help_text": "Enter one domain per line. These domains will be automatically rejected.",
            }
        ),
        help_text="Enter one domain per line. These domains will be automatically rejected.",
    )

    class Meta:
        model = None  # Will be set dynamically
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Store original values for change tracking
        if self.instance and self.instance.pk:
            self.original_whitelisted = set(self.instance.whitelisted_domains or [])
            self.original_blocklisted = set(self.instance.blocklisted_domains or [])

            if self.instance.whitelisted_domains:
                whitelisted_text = "\n".join(self.instance.whitelisted_domains)
                self.fields["whitelisted_domains_input"].initial = whitelisted_text

            if self.instance.blocklisted_domains:
                blocklisted_text = "\n".join(self.instance.blocklisted_domains)
                self.fields["blocklisted_domains_input"].initial = blocklisted_text
        else:
            self.original_whitelisted = set()
            self.original_blocklisted = set()

    def clean_whitelisted_domains_input(self):
        """Clean and validate whitelisted domains input"""
        data = self.cleaned_data.get("whitelisted_domains_input", "")
        if not data:
            return []

        # Split by lines and clean
        domains = [domain.strip() for domain in data.split("\n") if domain.strip()]

        # Validate domain format
        for domain in domains:
            if not self._is_valid_domain(domain):
                raise forms.ValidationError(f"Invalid domain format: {domain}")

        return domains

    def clean_blocklisted_domains_input(self):
        """Clean and validate blocklisted domains input"""
        data = self.cleaned_data.get("blocklisted_domains_input", "")
        if not data:
            return []

        # Split by lines and clean
        domains = [domain.strip() for domain in data.split("\n") if domain.strip()]

        # Validate domain format
        for domain in domains:
            if not self._is_valid_domain(domain):
                raise forms.ValidationError(f"Invalid domain format: {domain}")

        return domains

    def _is_valid_domain(self, domain):
        """Basic domain validation"""
        if not domain:
            return False

        # Check for basic domain format (simplified validation)
        parts = domain.split(".")
        if len(parts) < 2:
            return False

        # Check that parts are not empty and contain valid characters
        for part in parts:
            if not part or not part.replace("-", "").replace("_", "").isalnum():
                return False

        return True

    def get_domain_changes(self):
        """Get detailed information about domain changes"""
        if not hasattr(self, "original_whitelisted"):
            return {}

        new_whitelisted = set(self.cleaned_data.get("whitelisted_domains_input", []))
        new_blocklisted = set(self.cleaned_data.get("blocklisted_domains_input", []))

        changes = {
            "whitelisted_added": list(new_whitelisted - self.original_whitelisted),
            "whitelisted_removed": list(self.original_whitelisted - new_whitelisted),
            "blocklisted_added": list(new_blocklisted - self.original_blocklisted),
            "blocklisted_removed": list(self.original_blocklisted - new_blocklisted),
        }

        return changes

    def save(self, commit=True):
        """Save the form data to the model"""
        instance = super().save(commit=False)

        # Update the JSON fields with the cleaned domain lists
        instance.whitelisted_domains = self.cleaned_data.get(
            "whitelisted_domains_input", []
        )
        instance.blocklisted_domains = self.cleaned_data.get(
            "blocklisted_domains_input", []
        )

        if commit:
            instance.save()

        return instance

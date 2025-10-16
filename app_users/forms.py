from django import forms
from .models import User
from bitbio.countries import COUNTRIES
from .domain_management import should_block_registration, get_email_domain
import json


class UserLoginForm(forms.Form):
    """
    Form for user login using email and password.
    """

    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-input"}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )


class UserRegistrationForm(forms.Form):
    # User details fields
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    email = forms.EmailField(
        required=True, widget=forms.EmailInput(attrs={"class": "form-input"})
    )
    job_title = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-input"})
    )

    # Billing information fields
    company_trading_name = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_address_line_1 = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_state = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_country = forms.ChoiceField(
        choices=[("", "")] + [(country, country) for country in COUNTRIES],
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    billing_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    # Shipping information fields
    shipping_address_line_1 = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_city = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_state = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_country = forms.ChoiceField(
        choices=[("", "")] + [(country, country) for country in COUNTRIES],
        required=True,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    shipping_phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_instructions = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-input", "rows": "4"}),
        required=False,
    )

    # Boolean fields
    institution_tax_vat = forms.BooleanField(required=False)
    in_vitro = forms.BooleanField(required=False)
    in_vivo = forms.BooleanField(required=False)
    communications_agreement = forms.BooleanField(required=False)

    def clean_email(self):
        """Custom validation for email field"""
        email = self.cleaned_data.get("email")

        # Check if email is already registered
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                f"An account with this email address already exists. "
                f"If you already have an account, please sign in instead. "
                f"If you forgot your password, please contact support."
            )

        # Check if email domain is blocked
        if email and should_block_registration(email):
            domain = get_email_domain(email)
            raise forms.ValidationError(
                f"Registration not allowed for personal email domains. "
                f"Please use an institutional email address instead of {domain}. "
                f"If you're affiliated with a research institution, university, "
                f"or biotechnology company, please use your official email address."
            )
        return email

    def clean(self):
        cleaned_data = super().clean()

        # Validate passwords match
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        # Validate that at least one use intent is selected
        in_vitro = cleaned_data.get("in_vitro")
        in_vivo = cleaned_data.get("in_vivo")

        if not in_vitro and not in_vivo:
            raise forms.ValidationError(
                "Please select at least one use intent (in vitro or in vivo)."
            )

        return cleaned_data

    def save(self, commit=True):
        # Create user manually since we're not inheriting from UserCreationForm
        user = User.objects.create_user(
            email=self.cleaned_data["email"],
            password=self.cleaned_data["password1"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            job_title=self.cleaned_data["job_title"],
        )

        # Set billing information as JSON
        billing_info = {
            "company_trading_name": self.cleaned_data["company_trading_name"],
            "address_line_1": self.cleaned_data["billing_address_line_1"],
            "address_line_2": self.cleaned_data["billing_address_line_2"],
            "city": self.cleaned_data["billing_city"],
            "postal_code": self.cleaned_data["billing_postal_code"],
            "state": self.cleaned_data["billing_state"],
            "country": self.cleaned_data["billing_country"],
            "phone_number": self.cleaned_data["billing_phone"],
        }
        user.billing_information = billing_info

        # Set shipping information as JSON
        shipping_info = {
            "address_line_1": self.cleaned_data["shipping_address_line_1"],
            "address_line_2": self.cleaned_data["shipping_address_line_2"],
            "city": self.cleaned_data["shipping_city"],
            "postal_code": self.cleaned_data["shipping_postal_code"],
            "state": self.cleaned_data["shipping_state"],
            "country": self.cleaned_data["shipping_country"],
            "phone_number": self.cleaned_data["shipping_phone"],
            "instructions_restrictions": self.cleaned_data["shipping_instructions"],
        }
        user.shipping_information = shipping_info

        # Set boolean fields
        user.institution_tax_vat = self.cleaned_data["institution_tax_vat"]
        user.in_vitro = self.cleaned_data["in_vitro"]
        user.in_vivo = self.cleaned_data["in_vivo"]
        user.communications_agreement = self.cleaned_data["communications_agreement"]
        user.is_client = True

        if commit:
            user.save()
        return user


class UserProfileUpdateForm(forms.ModelForm):
    """Profile update form including user, billing, shipping and flags"""

    # Basic
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={"class": "form-input", "readonly": "readonly"}),
    )
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    job_title = forms.CharField(
        max_length=200,
        required=True,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    # Billing
    company_trading_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    billing_country = forms.ChoiceField(
        choices=[("", "")] + [(country, country) for country in COUNTRIES],
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    billing_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )

    # Shipping
    shipping_address_line_1 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_address_line_2 = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_postal_code = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_state = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_country = forms.ChoiceField(
        choices=[("", "")] + [(country, country) for country in COUNTRIES],
        required=False,
        widget=forms.Select(attrs={"class": "form-input"}),
    )
    shipping_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-input"}),
    )
    shipping_instructions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"class": "form-input", "rows": "3"}),
    )

    # Flags
    institution_tax_vat = forms.BooleanField(required=False)
    in_vitro = forms.BooleanField(required=False)
    in_vivo = forms.BooleanField(required=False)
    communications_agreement = forms.BooleanField(required=False)

    # Password change (optional)
    current_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        label="Current password",
    )
    new_password1 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        label="New password",
    )
    new_password2 = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        label="Confirm new password",
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "job_title",
            # Booleans
            "institution_tax_vat",
            "in_vitro",
            "in_vivo",
            "communications_agreement",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance
        if user:
            # Populate email explicitly
            self.fields["email"].initial = user.email
            # Billing
            billing = user.get_billing_info()
            self.fields["company_trading_name"].initial = billing.get(
                "company_trading_name", ""
            )
            self.fields["billing_address_line_1"].initial = billing.get(
                "address_line_1", ""
            )
            self.fields["billing_address_line_2"].initial = billing.get(
                "address_line_2", ""
            )
            self.fields["billing_city"].initial = billing.get("city", "")
            self.fields["billing_postal_code"].initial = billing.get("postal_code", "")
            self.fields["billing_state"].initial = billing.get("state", "")
            self.fields["billing_country"].initial = billing.get("country", "")
            self.fields["billing_phone"].initial = billing.get("phone_number", "")
            # Shipping
            shipping = user.get_shipping_info()
            self.fields["shipping_address_line_1"].initial = shipping.get(
                "address_line_1", ""
            )
            self.fields["shipping_address_line_2"].initial = shipping.get(
                "address_line_2", ""
            )
            self.fields["shipping_city"].initial = shipping.get("city", "")
            self.fields["shipping_postal_code"].initial = shipping.get(
                "postal_code", ""
            )
            self.fields["shipping_state"].initial = shipping.get("state", "")
            self.fields["shipping_country"].initial = shipping.get("country", "")
            self.fields["shipping_phone"].initial = shipping.get("phone_number", "")
            self.fields["shipping_instructions"].initial = shipping.get(
                "instructions_restrictions", ""
            )

    def clean(self):
        cleaned = super().clean()
        current_pw = cleaned.get("current_password")
        new_pw1 = cleaned.get("new_password1")
        new_pw2 = cleaned.get("new_password2")

        # Validate password change only if any field is provided
        if current_pw or new_pw1 or new_pw2:
            if not current_pw:
                self.add_error(
                    "current_password", "Please enter your current password."
                )
            if not new_pw1:
                self.add_error("new_password1", "Please enter a new password.")
            if not new_pw2:
                self.add_error("new_password2", "Please confirm your new password.")

            if self.errors:
                return cleaned

            user = self.instance
            if not user or not user.check_password(current_pw):
                self.add_error("current_password", "Current password is incorrect.")
                return cleaned

            if new_pw1 != new_pw2:
                self.add_error("new_password2", "New passwords do not match.")
                return cleaned

            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError

            try:
                validate_password(new_pw1, user)
            except ValidationError as ve:
                self.add_error("new_password1", ve)
                return cleaned

            cleaned["password_to_set"] = new_pw1

        return cleaned

    def save(self, commit=True):
        user: User = super().save(commit=False)
        # Email kept read-only in template; do not change programmatically for safety
        # Update billing
        billing_info = user.get_billing_info()
        billing_info.update(
            {
                "company_trading_name": self.cleaned_data.get(
                    "company_trading_name", ""
                ),
                "address_line_1": self.cleaned_data.get("billing_address_line_1", ""),
                "address_line_2": self.cleaned_data.get("billing_address_line_2", ""),
                "city": self.cleaned_data.get("billing_city", ""),
                "postal_code": self.cleaned_data.get("billing_postal_code", ""),
                "state": self.cleaned_data.get("billing_state", ""),
                "country": self.cleaned_data.get("billing_country", ""),
                "phone_number": self.cleaned_data.get("billing_phone", ""),
            }
        )
        user.billing_information = billing_info
        # Update shipping
        shipping_info = user.get_shipping_info()
        shipping_info.update(
            {
                "address_line_1": self.cleaned_data.get("shipping_address_line_1", ""),
                "address_line_2": self.cleaned_data.get("shipping_address_line_2", ""),
                "city": self.cleaned_data.get("shipping_city", ""),
                "postal_code": self.cleaned_data.get("shipping_postal_code", ""),
                "state": self.cleaned_data.get("shipping_state", ""),
                "country": self.cleaned_data.get("shipping_country", ""),
                "phone_number": self.cleaned_data.get("shipping_phone", ""),
                "instructions_restrictions": self.cleaned_data.get(
                    "shipping_instructions", ""
                ),
            }
        )
        user.shipping_information = shipping_info
        # Handle password change if requested (already validated in clean)
        password_to_set = self.cleaned_data.get("password_to_set")
        if password_to_set:
            user.set_password(password_to_set)

        if commit:
            user.save()
        return user


class PasswordResetForm(forms.Form):
    """Form for resetting password with token validation"""

    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        label="Password",
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={"class": "form-input"}),
        label="Confirm Password",
    )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match.")

        # Validate password strength
        if password1:
            from django.contrib.auth.password_validation import validate_password
            from django.core.exceptions import ValidationError

            try:
                # Create a temporary user object for password validation
                temp_user = User(email="temp@example.com")
                validate_password(password1, temp_user)
            except ValidationError as ve:
                raise forms.ValidationError(
                    ve.messages[0]
                    if ve.messages
                    else "Password doesn't meet requirements."
                )

        return cleaned_data

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using email.
    Note: The 'username' parameter is used by Django's authentication system,
    but we treat it as an email address.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(User.USERNAME_FIELD)

        if username is None or password is None:
            return None

        try:
            # Find user by email (case-insensitive)
            user = User.objects.get(email__iexact=username)
        except User.DoesNotExist:
            return None

        # Check if user can authenticate and has approved status
        if user.check_password(password) and self.user_can_authenticate(user):
            # Only allow users with approved status to log in
            if user.status == "approved":
                return user
            else:
                # Return None for non-approved users (this will cause authentication to fail)
                return None

    def user_can_authenticate(self, user):
        """
        Override to check both Django's default conditions and our approval status
        """
        # First check Django's default authentication conditions
        if not super().user_can_authenticate(user):
            return False

        # Then check our custom approval status
        return user.status == "approved"

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

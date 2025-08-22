"""
Admin Access Middleware for BitBio Django Project

This middleware provides additional security for admin routes by ensuring
only superusers and staff members can access admin-related URLs.
"""

from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from django.utils.translation import gettext_lazy as _


class AdminAccessMiddleware:
    """
    Middleware to restrict admin access to superusers and staff members only.
    This provides an additional layer of security beyond Django's built-in admin permissions.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if the request is for admin routes
        if request.path.startswith("/admin/"):
            # Allow access to login page
            if request.path == "/admin/login/":
                return self.get_response(request)

            # Check if user is authenticated and has proper permissions
            if not request.user.is_authenticated:
                # Redirect to admin login if not authenticated
                return redirect(reverse("admin:login"))

            # Check if user has admin access
            if not (
                request.user.is_active
                and (request.user.is_staff or request.user.is_superuser)
            ):
                # User doesn't have admin access
                messages.error(
                    request,
                    _(
                        "Access denied. You do not have permission to access the admin site."
                    ),
                )
                return redirect("/")  # Redirect to home page

        response = self.get_response(request)
        return response

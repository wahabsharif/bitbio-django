from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect


class ApprovalStatusMiddleware:
    """
    Middleware to check if logged-in users still have approved status.
    Automatically logs out users if their approval status changes.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and not on login/registration pages
        if (
            request.user.is_authenticated
            and not request.path.startswith("/admin/")
            and request.path not in ["/", "/registration/", "/registration/success/"]
        ):

            # Check if user's approval status is still approved
            if request.user.status != "approved":
                # Log out the user
                logout(request)
                messages.warning(
                    request,
                    "Your account approval status has changed. You have been logged out.",
                )
                return redirect("/")

        response = self.get_response(request)
        return response

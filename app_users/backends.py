from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.conf import settings
import requests
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

# Import ShopifyUserSession model
try:
    from .models import ShopifyUserSession
except ImportError:
    # Fallback for when the model doesn't exist yet
    ShopifyUserSession = None


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
        """
        For Shopify-only authentication, we don't store users in the database.
        This method returns None to force re-authentication on each request,
        ensuring we always validate with Shopify API.
        """
        # Return None to force re-authentication with Shopify API
        # This ensures we always validate credentials with Shopify, not local database
        return None


class ShopifyBackend(ModelBackend):
    """
    Custom authentication backend for Shopify Admin API authentication.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using email/password against Shopify Admin API.
        """
        if not username or not password:
            return None

        try:
            # First verify Shopify customer credentials
            verification_result = self._verify_shopify_credentials(username, password)
            if not verification_result[0]:
                logger.info(
                    f"Shopify customer verification failed for email: {username}"
                )
                # Store the error message for display to user
                self._last_auth_error = (
                    verification_result[2]
                    if len(verification_result) > 2
                    else "Authentication failed"
                )
                return None

            customer_data = verification_result[1]
            logger.info(f"Shopify authentication successful for: {username}")

            # Check if customer_data is valid
            if not customer_data:
                logger.error(f"No customer data returned for: {username}")
                return None

            # Store ONLY in ShopifyUserSession - do NOT create User record
            shopify_customer_id = customer_data.get("id")

            # Validate required data
            if not shopify_customer_id:
                logger.error(f"No Shopify customer ID found for: {username}")
                return None

            # Create or update ShopifyUserSession WITHOUT creating User
            if ShopifyUserSession:
                shopify_session, created = ShopifyUserSession.objects.update_or_create(
                    shopify_email=username,
                    defaults={
                        "shopify_customer_id": shopify_customer_id,
                        "shopify_first_name": customer_data.get("first_name", ""),
                        "shopify_last_name": customer_data.get("last_name", ""),
                        "shopify_verified_email": customer_data.get(
                            "verified_email", False
                        ),
                    },
                )
                logger.info(
                    f"{'Created' if created else 'Updated'} ShopifyUserSession for: {username}"
                )

                # Create a temporary in-memory User object for Django's authentication
                # This is NOT saved to the database
                user = User()
                user.pk = shopify_session.pk  # Use ShopifyUserSession ID
                user.email = shopify_session.shopify_email
                user.first_name = shopify_session.shopify_first_name
                user.last_name = shopify_session.shopify_last_name
                user.is_active = True
                user.is_staff = False
                user.is_superuser = False
                user.status = "approved"
                user.is_email_verified = shopify_session.shopify_verified_email

                # Mark as unsaved and override save to prevent DB writes
                user._state.adding = False
                user._is_shopify_only = True

                def no_op_save(*args, **kwargs):
                    """Prevent saving to database"""
                    logger.debug(
                        f"Blocked save attempt for Shopify-only user: {user.email}"
                    )
                    pass

                user.save = no_op_save

                logger.info(
                    f"Shopify authentication successful (session-only): {username}"
                )
                return user
            else:
                logger.error("ShopifyUserSession model not available")
                return None

        except Exception as e:
            logger.error(f"Error authenticating user {username}: {str(e)}")
            return None

    def _verify_shopify_credentials(self, email, password):
        """
        Verify Shopify customer credentials using Storefront API.
        This uses Shopify's customerAccessTokenCreate mutation to properly validate credentials.
        """
        try:
            # Use Shopify Storefront API for customer authentication
            storefront_url = (
                f"https://{settings.SHOPIFY_SHOP_DOMAIN}/api/2023-10/graphql.json"
            )

            headers = {
                "X-Shopify-Storefront-Access-Token": settings.SHOPIFY_STOREFRONT_ACCESS_TOKEN,
                "Content-Type": "application/json",
            }

            # GraphQL mutation to create customer access token (authenticates credentials)
            mutation = """
                    mutation customerAccessTokenCreate($input: CustomerAccessTokenCreateInput!) { customerAccessTokenCreate(input: $input) { customerAccessToken { accessToken expiresAt } customerUserErrors { field message } } }
            """

            variables = {"input": {"email": email, "password": password}}

            payload = {"query": mutation, "variables": variables}

            response = requests.post(storefront_url, headers=headers, json=payload)

            # Debug logging
            logger.info(f"Shopify API Response Status: {response.status_code}")
            logger.info(f"Shopify API Response Headers: {dict(response.headers)}")

            response.raise_for_status()

            data = response.json()
            logger.info(f"Shopify API Response Data: {data}")

            # Check for GraphQL errors
            if "errors" in data:
                logger.error(f"GraphQL errors: {data['errors']}")
                return (
                    False,
                    None,
                    "Authentication failed. Please check your credentials.",
                )

            # Check the mutation result
            customer_access_token_create = data.get("data", {}).get(
                "customerAccessTokenCreate", {}
            )
            customer_access_token = customer_access_token_create.get(
                "customerAccessToken"
            )
            customer_user_errors = customer_access_token_create.get(
                "customerUserErrors", []
            )

            if customer_access_token:
                # Authentication successful - get customer details
                logger.info(f"Shopify customer authenticated successfully: {email}")

                # Get customer details using the access token
                customer_data = self._get_customer_details_from_storefront(
                    customer_access_token["accessToken"]
                )
                return True, customer_data, None
            else:
                # Authentication failed - check if we should fallback to Admin API
                error_message = "Invalid email or password."
                error_code = None

                if customer_user_errors:
                    error_message = customer_user_errors[0].get(
                        "message", "Invalid email or password."
                    )
                    error_code = customer_user_errors[0].get("code")

                logger.info(
                    f"Shopify customer authentication failed for email: {email} - {error_message}"
                )

                # If customer is "Unidentified", try Admin API fallback
                if error_code == "UNIDENTIFIED_CUSTOMER":
                    logger.info(
                        "Customer unidentified in Storefront API, trying Admin API fallback"
                    )
                    return self._verify_shopify_credentials_admin_api(email, password)

                return False, None, error_message

        except requests.RequestException as e:
            logger.error(f"Error verifying Shopify customer credentials: {str(e)}")
            # Fallback to Admin API if Storefront API fails
            logger.info("Falling back to Admin API for customer verification")
            return self._verify_shopify_credentials_admin_api(email, password)
        except Exception as e:
            logger.error(f"Unexpected error during Shopify authentication: {str(e)}")
            # Fallback to Admin API if unexpected error occurs
            logger.info("Falling back to Admin API for customer verification")
            return self._verify_shopify_credentials_admin_api(email, password)

    def _verify_shopify_credentials_admin_api(self, email, password):
        """
        Fallback method using Admin API to verify customer exists.
        Note: Admin API doesn't support password verification, so we only check customer existence.
        """
        try:
            headers = {
                "X-Shopify-Access-Token": settings.SHOPIFY_ACCESS_TOKEN,
                "Content-Type": "application/json",
            }

            # Search for customer by email using Admin API
            search_url = f"https://{settings.SHOPIFY_SHOP_DOMAIN}/admin/api/2023-10/customers/search.json"
            params = {"query": f"email:{email}"}

            response = requests.get(search_url, headers=headers, params=params)

            # Debug logging for Admin API
            logger.info(f"Admin API Response Status: {response.status_code}")

            response.raise_for_status()

            data = response.json()
            logger.info(f"Admin API Response Data: {data}")
            customers = data.get("customers", [])

            if customers:
                customer = customers[0]
                logger.info(f"Customer found via Admin API for email: {email}")
                # Convert Admin API format to match Storefront API format
                customer_data = {
                    "id": customer.get("id"),
                    "email": customer.get("email"),
                    "first_name": customer.get("first_name", ""),
                    "last_name": customer.get("last_name", ""),
                    "verified_email": customer.get("verified_email", False),
                }
                return True, customer_data, None
            else:
                logger.info(f"No customer found via Admin API for email: {email}")
                return False, None, "No Shopify account found with this email address."

        except Exception as e:
            logger.error(f"Error in Admin API fallback: {str(e)}")
            return False, None, "Unable to verify credentials. Please try again later."

    def _get_customer_details_from_storefront(self, access_token):
        """
        Get customer details using the Storefront API access token.
        """
        try:
            storefront_url = (
                f"https://{settings.SHOPIFY_SHOP_DOMAIN}/api/2023-10/graphql.json"
            )

            headers = {
                "X-Shopify-Storefront-Access-Token": settings.SHOPIFY_STOREFRONT_ACCESS_TOKEN,
                "Content-Type": "application/json",
            }

            # GraphQL query to get customer details
            query = """
            query getCustomer($customerAccessToken: String!) {
                customer(customerAccessToken: $customerAccessToken) {
                    id
                    email
                    firstName
                    lastName
                    displayName
                    phone
                    createdAt
                    updatedAt
                }
            }
            """

            variables = {"customerAccessToken": access_token}

            payload = {"query": query, "variables": variables}

            response = requests.post(storefront_url, headers=headers, json=payload)
            response.raise_for_status()

            data = response.json()
            logger.info(f"Get customer details response: {data}")

            if "data" in data and data["data"] and data["data"].get("customer"):
                customer = data["data"]["customer"]
                # Convert Shopify Storefront API format to match Admin API format
                customer_info = {
                    "id": int(
                        customer["id"].split("/")[-1]
                    ),  # Extract numeric ID from GraphQL ID
                    "email": customer["email"],
                    "first_name": customer["firstName"] or "",
                    "last_name": customer["lastName"] or "",
                    "verified_email": True,  # If they can authenticate, email is verified
                }
                logger.info(f"Successfully extracted customer info: {customer_info}")
                return customer_info

            logger.warning(f"No customer data in response: {data}")
            return None

        except Exception as e:
            logger.error(
                f"Error getting customer details from Storefront API: {str(e)}"
            )
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
        """
        Retrieve user from ShopifyUserSession.
        For Shopify-only users, we fetch from shopify_user_session table.
        """
        try:
            if ShopifyUserSession:
                # Try to get from ShopifyUserSession first
                shopify_session = ShopifyUserSession.objects.get(pk=user_id)

                # Recreate in-memory User object
                user = User()
                user.pk = shopify_session.pk
                user.email = shopify_session.shopify_email
                user.first_name = shopify_session.shopify_first_name
                user.last_name = shopify_session.shopify_last_name
                user.is_active = True
                user.is_staff = False
                user.is_superuser = False
                user.status = "approved"
                user.is_email_verified = shopify_session.shopify_verified_email

                # Mark as unsaved and override save
                user._state.adding = False
                user._is_shopify_only = True

                def no_op_save(*args, **kwargs):
                    """Prevent saving to database"""
                    logger.debug(
                        f"Blocked save attempt for Shopify-only user: {user.email}"
                    )
                    pass

                user.save = no_op_save

                return user
        except Exception as e:
            logger.debug(
                f"Could not retrieve Shopify session for user_id {user_id}: {str(e)}"
            )

        return None

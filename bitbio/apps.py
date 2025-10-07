"""
Bitbio app configuration
"""

from django.apps import AppConfig


class BitbioConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bitbio"
    verbose_name = "BitBio Core"

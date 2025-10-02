# Generated migration for ShopifyUserSession changes

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("app_users", "0007_remove_user_shopify_access_token_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="shopifyusersession",
            name="user",
            field=models.OneToOneField(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="shopify_session",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name="shopifyusersession",
            name="shopify_customer_id",
            field=models.BigIntegerField(db_index=True, unique=True),
        ),
        migrations.AlterField(
            model_name="shopifyusersession",
            name="shopify_email",
            field=models.EmailField(db_index=True, max_length=254, unique=True),
        ),
        migrations.AddIndex(
            model_name="shopifyusersession",
            index=models.Index(fields=["shopify_email"], name="shopify_email_idx"),
        ),
    ]

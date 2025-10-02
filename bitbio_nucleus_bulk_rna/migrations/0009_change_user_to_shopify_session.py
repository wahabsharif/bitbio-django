# Generated migration to change User foreign keys to ShopifyUserSession

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("bitbio_nucleus_bulk_rna", "0007_genecollection_customer_visible_and_more"),
        ("app_users", "0008_alter_shopifyusersession_user_and_more"),
    ]

    operations = [
        # Remove old user fields
        migrations.RemoveField(
            model_name="usertier",
            name="user",
        ),
        migrations.RemoveField(
            model_name="usergenerequest",
            name="user",
        ),
        migrations.RemoveField(
            model_name="genecollection",
            name="created_by",
        ),
        # Add new shopify_session fields
        migrations.AddField(
            model_name="usertier",
            name="shopify_session",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                to="app_users.shopifyusersession",
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="usergenerequest",
            name="shopify_session",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to="app_users.shopifyusersession",
                default=1,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="genecollection",
            name="created_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="app_users.shopifyusersession",
            ),
        ),
    ]

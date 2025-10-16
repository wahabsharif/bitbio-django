from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_users", "0009_remove_user_from_shopify_session"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="password_reset_sent_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="user",
            name="password_reset_token",
            field=models.UUIDField(blank=True, db_index=True, null=True, unique=True),
        ),
    ]

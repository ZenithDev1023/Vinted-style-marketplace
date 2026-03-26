from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0007_listing_credit_awarded_on_sale"),
    ]

    operations = [
        migrations.AlterField(
            model_name="directmessage",
            name="content",
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name="directmessage",
            name="image",
            field=models.ImageField(blank=True, null=True, upload_to="messages/"),
        ),
    ]
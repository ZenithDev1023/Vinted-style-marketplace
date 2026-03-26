from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0006_directmessage"),
    ]

    operations = [
        migrations.AddField(
            model_name="listing",
            name="credit_awarded_on_sale",
            field=models.BooleanField(default=False),
        ),
    ]
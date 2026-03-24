from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("myapp", "0003_rename_created_at_listing_createddate_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ListingReview",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("rating", models.IntegerField()),
                ("comment", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("listing", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="myapp.listing")),
                ("reviewer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="myapp.user")),
            ],
        ),
    ]
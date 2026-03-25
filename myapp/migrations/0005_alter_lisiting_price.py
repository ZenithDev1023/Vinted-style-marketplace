from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_listingreview'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='price',
            field=models.DecimalField(decimal_places=2, max_digits=20),
        ),
    ]
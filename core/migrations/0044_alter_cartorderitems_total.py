# Generated by Django 5.1.2 on 2024-10-31 16:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0043_alter_cartorderitems_total_alter_order_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cartorderitems",
            name="total",
            field=models.DecimalField(decimal_places=2, editable=False, max_digits=10),
        ),
    ]
# Generated by Django 5.1.2 on 2024-10-30 02:06

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0041_alter_cartorderitems_price_alter_cartorderitems_qty_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="cartorderitems",
            name="image",
            field=models.ImageField(upload_to="products/"),
        ),
        migrations.AlterField(
            model_name="cartorderitems",
            name="total",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.CharField(
                choices=[
                    ("processing", "Processing"),
                    ("shipped", "Shipped"),
                    ("delivered", "Delivered"),
                    ("cancelled", "Cancelled"),
                ],
                default="processing",
                max_length=30,
            ),
        ),
    ]
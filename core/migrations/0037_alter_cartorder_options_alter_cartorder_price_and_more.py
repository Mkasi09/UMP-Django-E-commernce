# Generated by Django 4.2.7 on 2024-10-29 09:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0036_product_price"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cartorder",
            options={"verbose_name_plural": "Cart Orders"},
        ),
        migrations.AlterField(
            model_name="cartorder",
            name="price",
            field=models.DecimalField(decimal_places=2, default=1.99, max_digits=10),
        ),
        migrations.AlterField(
            model_name="cartorder",
            name="product_status",
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
        migrations.AlterField(
            model_name="cartorderitems",
            name="price",
            field=models.DecimalField(decimal_places=2, default=1.99, max_digits=10),
        ),
        migrations.AlterField(
            model_name="cartorderitems",
            name="product_status",
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
        migrations.AlterField(
            model_name="cartorderitems",
            name="total",
            field=models.DecimalField(decimal_places=2, default=1.99, max_digits=10),
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("order_number", models.CharField(max_length=10, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(default="Pending", max_length=20)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]

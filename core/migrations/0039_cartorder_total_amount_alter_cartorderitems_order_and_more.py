# Generated by Django 5.1.2 on 2024-10-29 21:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0038_alter_payment_payfast_id_alter_payment_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="cartorder",
            name="total_amount",
            field=models.DecimalField(decimal_places=2, default=1, max_digits=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="cartorderitems",
            name="order",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.order"
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="order_number",
            field=models.CharField(max_length=20, unique=True),
        ),
    ]

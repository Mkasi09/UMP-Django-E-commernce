# Generated by Django 4.2.1 on 2023-11-10 07:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_remove_product_mfd_remove_product_product_life_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='shipping',
            field=models.CharField(blank=True, default='1', max_length=100, null=True),
        ),
    ]

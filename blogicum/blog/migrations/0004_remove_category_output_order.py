# Generated by Django 3.2.16 on 2024-10-25 08:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0003_category_output_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='output_order',
        ),
    ]

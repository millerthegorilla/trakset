# Generated by Django 5.1.11 on 2025-07-05 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trakset', '0013_alter_asset_status'),
    ]

    operations = [
        migrations.RenameField(
            model_name='status',
            old_name='status',
            new_name='type',
        ),
    ]

# Generated by Django 5.0 on 2024-01-01 17:18

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0004_etatstock'),
    ]

    operations = [
        migrations.RenameField(
            model_name='etatstock',
            old_name='produitS',
            new_name='produit',
        ),
        migrations.AddField(
            model_name='etatstock',
            name='date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]

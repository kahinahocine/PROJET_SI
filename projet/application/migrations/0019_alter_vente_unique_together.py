# Generated by Django 5.0 on 2024-01-07 13:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0018_alter_vente_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='vente',
            unique_together=set(),
        ),
    ]

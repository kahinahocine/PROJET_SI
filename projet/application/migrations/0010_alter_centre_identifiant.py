# Generated by Django 5.0 on 2024-01-04 16:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0009_centre_identifiant_pv'),
    ]

    operations = [
        migrations.AlterField(
            model_name='centre',
            name='identifiant',
            field=models.CharField(default='valeur_par_defaut', max_length=10, unique=True),
        ),
    ]

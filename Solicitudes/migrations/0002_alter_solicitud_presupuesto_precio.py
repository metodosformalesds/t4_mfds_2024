# Generated by Django 4.2.16 on 2024-11-04 22:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Solicitudes', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='solicitud_presupuesto',
            name='precio',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]

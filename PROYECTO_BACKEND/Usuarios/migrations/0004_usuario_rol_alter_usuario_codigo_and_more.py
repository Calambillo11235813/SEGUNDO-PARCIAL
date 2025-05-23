# Generated by Django 5.2.1 on 2025-05-19 16:13

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Permisos', '0002_initial'),
        ('Usuarios', '0003_remove_contrasena'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='rol',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='usuarios_rol', to='Permisos.rol'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='codigo',
            field=models.CharField(max_length=20, unique=True, verbose_name='Código de acceso'),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefono',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
    ]

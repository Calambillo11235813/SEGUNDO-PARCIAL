# Generated by Django 5.2.1 on 2025-05-17 17:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Usuarios', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='codigo',
            field=models.CharField(default=101, max_length=10, unique=True, verbose_name='Código de acceso'),
            preserve_default=False,
        ),
    ]

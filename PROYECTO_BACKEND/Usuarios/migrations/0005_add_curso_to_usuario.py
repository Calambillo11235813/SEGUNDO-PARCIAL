# Generated by Django 5.2.1 on 2025-05-26 02:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Cursos', '0008_add_curso_to_usuario'),
        ('Usuarios', '0004_usuario_rol_alter_usuario_codigo_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='estudiante',
            name='curso',
        ),
        migrations.AddField(
            model_name='usuario',
            name='curso',
            field=models.ForeignKey(blank=True, help_text='Curso al que pertenece el estudiante (solo para estudiantes)', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='estudiantes_usuarios', to='Cursos.curso'),
        ),
    ]

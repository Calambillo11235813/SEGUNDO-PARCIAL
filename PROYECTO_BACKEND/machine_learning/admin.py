from django.contrib import admin
from machine_learning.models import DatasetAcademico, ModeloML, PrediccionAcademica, RegistroEstudianteML

@admin.register(DatasetAcademico)
class DatasetAcademicoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'año_inicio', 'año_fin', 'total_registros', 'fecha_creacion', 'activo']
    list_filter = ['activo', 'año_inicio', 'año_fin']
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

@admin.register(ModeloML)
class ModeloMLAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'algoritmo', 'mae_score', 'r2_score', 'fecha_entrenamiento', 'activo']
    list_filter = ['algoritmo', 'activo', 'fecha_entrenamiento']
    search_fields = ['nombre']
    readonly_fields = ['id', 'fecha_entrenamiento']

@admin.register(PrediccionAcademica)
class PrediccionAcademicaAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'prediccion_numerica', 'nivel_rendimiento', 'confianza', 'fecha_prediccion']
    list_filter = ['nivel_rendimiento', 'fecha_prediccion']
    search_fields = ['estudiante__codigo', 'estudiante__first_name', 'estudiante__last_name']
    readonly_fields = ['id', 'fecha_prediccion']

@admin.register(RegistroEstudianteML)
class RegistroEstudianteMLAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'trimestre', 'promedio_notas_anterior', 'rendimiento_futuro']
    list_filter = ['trimestre__año_academico']
    search_fields = ['estudiante__codigo']

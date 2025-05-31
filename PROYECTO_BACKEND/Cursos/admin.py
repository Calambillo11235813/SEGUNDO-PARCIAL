from django.contrib import admin
from .models import Trimestre, PromedioTrimestral, PromedioAnual

@admin.register(Trimestre)
class TrimestreAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'numero', 'año_academico', 'fecha_inicio', 'fecha_fin', 'estado', 'esta_activo']
    list_filter = ['año_academico', 'numero', 'estado']
    search_fields = ['nombre', 'año_academico']
    ordering = ['-año_academico', 'numero']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(PromedioTrimestral)
class PromedioTrimestralAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'materia', 'trimestre', 'promedio_final', 'porcentaje_asistencia', 'aprobado']
    list_filter = ['trimestre__año_academico', 'trimestre__numero', 'aprobado', 'materia__curso']
    search_fields = ['estudiante__nombre', 'estudiante__apellido', 'materia__nombre']
    readonly_fields = ['fecha_calculo', 'created_at']

@admin.register(PromedioAnual)
class PromedioAnualAdmin(admin.ModelAdmin):
    list_display = ['estudiante', 'materia', 'año_academico', 'promedio_anual', 'aprobado_anual']
    list_filter = ['año_academico', 'aprobado_anual', 'materia__curso']
    search_fields = ['estudiante__nombre', 'estudiante__apellido', 'materia__nombre']
    readonly_fields = ['fecha_calculo', 'created_at']

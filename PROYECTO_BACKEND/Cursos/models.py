from django.db import models
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Nivel(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)

    class Meta:
        verbose_name = 'Nivel'
        verbose_name_plural = 'Niveles'

    def __str__(self):
        return self.nombre

class Curso(models.Model):
    id = models.AutoField(primary_key=True)
    grado = models.IntegerField()
    paralelo = models.CharField(max_length=1)  # Ahora puede ser 'A', 'B', etc.
    nivel = models.ForeignKey(Nivel, on_delete=models.CASCADE, related_name='cursos')

    class Meta:
        verbose_name = 'Curso'
        verbose_name_plural = 'Cursos'
        unique_together = ('nivel', 'grado', 'paralelo')

    def __str__(self):
        # Actualizamos también la representación en string
        return f"{self.nivel} - {self.grado}° {self.paralelo}"

class Materia(models.Model):
    nombre = models.CharField(max_length=100)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE)
    profesor = models.ForeignKey(
        'Usuarios.Usuario',  # Referencia al modelo Usuario en la app Usuarios
        on_delete=models.SET_NULL,  # Si se elimina el profesor, la materia queda sin profesor
        null=True,           # Permite que una materia no tenga profesor asignado
        blank=True,
        related_name='materias_asignadas'  # Para acceder fácilmente a las materias de un profesor
    )
    
    class Meta:
        unique_together = ('nombre', 'curso')
    
    def __str__(self):
        return f"{self.nombre} - {self.curso}"

class Notas(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=4, decimal_places=2)
    concepto = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    # Cambiar a Usuario con validación de rol
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, 
                                  related_name='notas',
                                  limit_choices_to={'rol__nombre': 'Estudiante'})
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='notas')

    class Meta:
        verbose_name = 'Nota'
        verbose_name_plural = 'Notas'

    def __str__(self):
        return f"Nota {self.id}: {self.valor} - {self.materia} - {self.estudiante}"

class Boletin(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    periodo = models.CharField(max_length=50)
    # Cambiar a Usuario con validación de rol
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, 
                                  related_name='boletines',
                                  limit_choices_to={'rol__nombre': 'Estudiante'})
    notas = models.ManyToManyField(Notas, related_name='boletines')

    class Meta:
        verbose_name = 'Boletín'
        verbose_name_plural = 'Boletines'

    def __str__(self):
        return f"Boletín {self.id}: {self.estudiante} - {self.periodo}"

class Asistencia(models.Model):
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, related_name='asistencias')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='asistencias')
    trimestre = models.ForeignKey('Trimestre', on_delete=models.CASCADE, related_name='asistencias')  # ✅ CORREGIDO
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True)
    justificada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ('estudiante', 'materia', 'fecha')
        ordering = ['-fecha']
    
    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        if not self.presente and self.justificada:
            estado = "Justificado"
        return f"{self.estudiante} - {self.materia} - {self.fecha} - {estado}"

    def save(self, *args, **kwargs):
        """
        Auto-asigna el trimestre basado en la fecha si no se proporciona
        """
        if not self.trimestre:
            # Buscar el trimestre activo que contenga esta fecha
            trimestre_activo = Trimestre.objects.filter(  # ✅ Aquí también usar referencia como string si es necesario
                fecha_inicio__lte=self.fecha,
                fecha_fin__gte=self.fecha,
                activo=True
            ).first()
            
            if trimestre_activo:
                self.trimestre = trimestre_activo
            else:
                from django.core.exceptions import ValidationError
                raise ValidationError("No existe un trimestre activo para la fecha especificada")
        
        super().save(*args, **kwargs)

class Trimestre(models.Model):
    """
    Representa un trimestre académico dentro del año escolar.
    """
    ESTADO_CHOICES = [
        ('PLANIFICADO', 'Planificado'),
        ('ACTIVO', 'Activo'),
        ('FINALIZADO', 'Finalizado'),
        ('CERRADO', 'Cerrado'),
    ]
    
    numero = models.IntegerField(choices=[(1, 'Primer Trimestre'), (2, 'Segundo Trimestre'), (3, 'Tercer Trimestre')])
    nombre = models.CharField(max_length=50, help_text="Ej: Primer Trimestre 2025")
    año_academico = models.IntegerField(help_text="Año académico al que pertenece")
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    fecha_limite_evaluaciones = models.DateField(help_text="Fecha límite para registrar evaluaciones")
    fecha_limite_calificaciones = models.DateField(help_text="Fecha límite para registrar calificaciones")
    
    # Configuración académica
    nota_minima_aprobacion = models.DecimalField(max_digits=5, decimal_places=2, default=51.0)
    porcentaje_asistencia_minima = models.DecimalField(max_digits=5, decimal_places=2, default=80.0)
    
    # Estado del trimestre
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='PLANIFICADO')
    activo = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, related_name='trimestres_creados', null=True, blank=True)

    class Meta:
        db_table = 'trimestres'
        verbose_name = 'Trimestre'
        verbose_name_plural = 'Trimestres'
        unique_together = ('numero', 'año_academico')
        ordering = ['año_academico', 'numero']

    def __str__(self):
        return f"{self.nombre} ({self.año_academico})"

    @property
    def esta_activo(self):
        """Verifica si el trimestre está en período activo"""
        from django.utils import timezone
        ahora = timezone.now().date()
        return self.fecha_inicio <= ahora <= self.fecha_fin and self.estado == 'ACTIVO'

    @property
    def puede_registrar_evaluaciones(self):
        """Verifica si aún se pueden registrar evaluaciones"""
        from django.utils import timezone
        return timezone.now().date() <= self.fecha_limite_evaluaciones and self.estado in ['PLANIFICADO', 'ACTIVO']

    @property
    def puede_registrar_calificaciones(self):
        """Verifica si aún se pueden registrar calificaciones"""
        from django.utils import timezone
        return timezone.now().date() <= self.fecha_limite_calificaciones and self.estado in ['ACTIVO', 'FINALIZADO']

class TipoEvaluacion(models.Model):
    """
    Define los tipos de evaluación disponibles en el sistema.
    """
    TIPOS_CHOICES = [
        ('EXAMEN', 'Examen'),
        ('PARTICIPACION', 'Participación en Clase'),
        ('TRABAJO', 'Trabajo Práctico'),
    ]
    
    nombre = models.CharField(max_length=50, choices=TIPOS_CHOICES, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tipos_evaluacion'
        verbose_name = 'Tipo de Evaluación'
        verbose_name_plural = 'Tipos de Evaluación'



class ConfiguracionEvaluacionMateria(models.Model):
    """
    Configura los tipos de evaluación aplicables para una materia específica
    con sus respectivos porcentajes de la nota final.
    """
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='configuraciones_evaluacion')
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    porcentaje = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Porcentaje que este tipo de evaluación representa en la nota final (0-100)"
    )
    activo = models.BooleanField(default=True)
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'Usuarios.Usuario', 
        on_delete=models.CASCADE, 
        related_name='configuraciones_evaluacion_creadas',
        null=True, 
        blank=True
    )

    class Meta:
        db_table = 'configuracion_evaluacion_materia'
        verbose_name = 'Configuración de Evaluación por Materia'
        verbose_name_plural = 'Configuraciones de Evaluación por Materias'
        unique_together = ['materia', 'tipo_evaluacion']

    def __str__(self):
        return f"{self.materia.nombre} - {self.tipo_evaluacion}: {self.porcentaje}%"

    def save(self, *args, **kwargs):
        """
        Sobrescribimos el método save para validar que la suma de porcentajes
        no exceda el 100% para la materia.
        """
        # Ejecutamos la validación solo si el objeto es nuevo o ha cambiado el porcentaje
        if not self.pk or ConfiguracionEvaluacionMateria.objects.get(pk=self.pk).porcentaje != self.porcentaje:
            # Calculamos la suma actual sin considerar este registro
            configuraciones = ConfiguracionEvaluacionMateria.objects.filter(
                materia=self.materia, 
                activo=True
            ).exclude(pk=self.pk)
            
            suma_actual = sum(conf.porcentaje for conf in configuraciones)
            
            # Validamos que no exceda el 100%
            if suma_actual + self.porcentaje > 100:
                from django.core.exceptions import ValidationError
                raise ValidationError(
                    f"La suma de porcentajes ({suma_actual + self.porcentaje}%) excede el 100%. "
                    f"Porcentaje disponible: {100 - suma_actual}%"
                )
        
        super().save(*args, **kwargs)





class EvaluacionBase(models.Model):
    """Clase base abstracta para todas las evaluaciones"""
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    materia = models.ForeignKey(
        Materia, 
        on_delete=models.CASCADE,
        related_name="%(class)s_evaluaciones"  # Esto se expandirá diferente para cada subclase
    )
    trimestre = models.ForeignKey(
        Trimestre, 
        on_delete=models.CASCADE, 
        null=True, blank=True,
        related_name="%(class)s_evaluaciones"  # Esto se expandirá diferente para cada subclase
    )
    tipo_evaluacion = models.ForeignKey(
        TipoEvaluacion, 
        on_delete=models.SET_NULL, 
        null=True
    )
    porcentaje_nota_final = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01')), MaxValueValidator(Decimal('100'))]
    )
    activo = models.BooleanField(default=True)
    publicado = models.BooleanField(default=False)
    
    class Meta:
        abstract = True  # Esta clase es abstracta, no se crea tabla en la BD

class EvaluacionEntregable(EvaluacionBase):
    """Para evaluaciones con fechas de entrega como exámenes y trabajos"""
    fecha_asignacion = models.DateField()
    fecha_entrega = models.DateField()
    fecha_limite = models.DateField(null=True, blank=True)
    nota_maxima = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    nota_minima_aprobacion = models.DecimalField(max_digits=5, decimal_places=2, default=51.00)
    permite_entrega_tardia = models.BooleanField(default=False)
    penalizacion_tardio = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    class Meta:
        db_table = 'evaluaciones_entregables'

class EvaluacionParticipacion(EvaluacionBase):
    """Específico para participación en clase"""
    fecha_registro = models.DateField()
    
    class Meta:
        db_table = 'evaluaciones_participacion'

class Calificacion(models.Model):
    """
    Almacena las calificaciones de los estudiantes en las evaluaciones.
    Puede referenciar cualquier tipo de evaluación (entregable o participación)
    """
    # Campos para la relación genérica
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    evaluacion = GenericForeignKey('content_type', 'object_id')
    
    # Otros campos que ya existían
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE)
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    nota_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Información de entrega
    fecha_entrega = models.DateTimeField(null=True, blank=True)
    entrega_tardia = models.BooleanField(default=False)
    penalizacion_aplicada = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    
    # Observaciones y feedback
    observaciones = models.TextField(blank=True, null=True)
    retroalimentacion = models.TextField(blank=True, null=True)
    
    # Estado
    finalizada = models.BooleanField(default=False)
    
    # Metadatos
    calificado_por = models.ForeignKey(
        'Usuarios.Usuario', 
        on_delete=models.CASCADE, 
        related_name='calificaciones_realizadas',
        null=True, 
        blank=True
    )
    fecha_calificacion = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'calificaciones'
        verbose_name = 'Calificación'
        verbose_name_plural = 'Calificaciones'
        unique_together = [('content_type', 'object_id', 'estudiante')]

    def __str__(self):
        evaluacion_titulo = getattr(self.evaluacion, 'titulo', 'Sin título')
        return f"{self.estudiante.nombre} - {evaluacion_titulo}: {self.nota}/{self.nota_sobre}"

    @property
    def nota_final(self):
        """Calcula la nota final aplicando penalizaciones"""
        if self.penalizacion_aplicada > 0:
            return max(0, self.nota - (self.nota * self.penalizacion_aplicada / 100))
        return self.nota

    @property
    def porcentaje(self):
        """Calcula el porcentaje obtenido"""
        if self.nota_sobre > 0:
            return (self.nota / self.nota_sobre) * 100
        return 0

    @property
    def esta_aprobado(self):
        """Determina si la calificación está aprobada"""
        # Adaptado para manejar cualquier tipo de evaluación
        if hasattr(self.evaluacion, 'nota_minima_aprobacion'):
            nota_minima = self.evaluacion.nota_minima_aprobacion
        else:
            # Valor por defecto si no tiene el atributo
            nota_minima = 51.0
        
        return self.nota_final >= nota_minima

class PromedioTrimestral(models.Model):
    """
    Almacena los promedios trimestrales de cada estudiante por materia.
    """
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, related_name='promedios_trimestrales')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='promedios_trimestrales')
    trimestre = models.ForeignKey(Trimestre, on_delete=models.CASCADE, related_name='promedios')
    
    # Calificaciones
    promedio_evaluaciones = models.DecimalField(max_digits=5, decimal_places=2, help_text="Promedio de evaluaciones del trimestre")
    promedio_final = models.DecimalField(max_digits=5, decimal_places=2, help_text="Promedio final considerando todos los factores")
    
    # Asistencia
    total_clases = models.IntegerField(default=0)
    asistencias = models.IntegerField(default=0)
    porcentaje_asistencia = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Estado académico
    aprobado = models.BooleanField(default=False)
    observaciones = models.TextField(blank=True, null=True)
    
    # Metadatos
    calculado_automaticamente = models.BooleanField(default=True)
    fecha_calculo = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'promedios_trimestrales'
        verbose_name = 'Promedio Trimestral'
        verbose_name_plural = 'Promedios Trimestrales'
        unique_together = ('estudiante', 'materia', 'trimestre')
        ordering = ['-trimestre__año_academico', '-trimestre__numero', 'materia__nombre']

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.materia.nombre} - {self.trimestre}"

    def calcular_promedio_final(self):
        """Calcula el promedio final considerando asistencia y evaluaciones"""
        if self.porcentaje_asistencia < self.trimestre.porcentaje_asistencia_minima:
            # Si no cumple asistencia mínima, automáticamente reprobado
            self.promedio_final = 0.0
            self.aprobado = False
        else:
            self.promedio_final = self.promedio_evaluaciones
            self.aprobado = self.promedio_final >= self.trimestre.nota_minima_aprobacion
        
        self.save()
        return self.promedio_final

class PromedioAnual(models.Model):
    """
    Almacena el promedio anual de cada estudiante por materia.
    """
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, related_name='promedios_anuales')
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='promedios_anuales')
    año_academico = models.IntegerField()
    
    # Promedios trimestrales
    promedio_trimestre_1 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    promedio_trimestre_2 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    promedio_trimestre_3 = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    # Promedio final anual
    promedio_anual = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    aprobado_anual = models.BooleanField(default=False)
    
    # Asistencia anual
    porcentaje_asistencia_anual = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # Metadatos
    calculado_automaticamente = models.BooleanField(default=True)
    fecha_calculo = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'promedios_anuales'
        verbose_name = 'Promedio Anual'
        verbose_name_plural = 'Promedios Anuales'
        unique_together = ('estudiante', 'materia', 'año_academico')
        ordering = ['-año_academico', 'materia__nombre']

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.materia.nombre} - {self.año_academico}"

    def calcular_promedio_anual(self):
        """Calcula el promedio anual basado en los tres trimestres"""
        promedios = [p for p in [self.promedio_trimestre_1, self.promedio_trimestre_2, self.promedio_trimestre_3] if p is not None]
        
        if promedios:
            self.promedio_anual = sum(promedios) / len(promedios)
            self.aprobado_anual = self.promedio_anual >= 51.0  # Nota mínima Bolivia
        else:
            self.promedio_anual = 0.0
            self.aprobado_anual = False
        
        self.save()
        return self.promedio_anual

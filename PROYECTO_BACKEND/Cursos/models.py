from django.db import models
from django.utils import timezone

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
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True)
    justificada = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Asistencia'
        verbose_name_plural = 'Asistencias'
        unique_together = ('estudiante', 'materia', 'fecha')  # Un estudiante solo puede tener una asistencia por materia y fecha
        ordering = ['-fecha']  # Ordenar por fecha descendente
    
    def __str__(self):
        estado = "Presente" if self.presente else "Ausente"
        if not self.presente and self.justificada:
            estado = "Justificado"
        return f"{self.estudiante} - {self.materia} - {self.fecha} - {estado}"

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

    def __str__(self):
        return self.get_nombre_display()

class Evaluacion(models.Model):
    """
    Representa una evaluación específica (examen, trabajo, etc.) para una materia.
    """
    materia = models.ForeignKey(Materia, on_delete=models.CASCADE, related_name='evaluaciones')
    tipo_evaluacion = models.ForeignKey(TipoEvaluacion, on_delete=models.CASCADE)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha_asignacion = models.DateField()
    fecha_entrega = models.DateField()
    fecha_limite = models.DateField(null=True, blank=True, help_text="Fecha límite para entrega tardía")
    
    # Configuración de calificación
    nota_maxima = models.DecimalField(max_digits=5, decimal_places=2, default=100.00)
    nota_minima_aprobacion = models.DecimalField(max_digits=5, decimal_places=2, default=51.00)
    porcentaje_nota_final = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text="Porcentaje que representa en la nota final de la materia"
    )
    
    # Configuración de entrega
    permite_entrega_tardia = models.BooleanField(default=False)
    penalizacion_tardio = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=0.00,
        help_text="Porcentaje de penalización por entrega tardía"
    )
    
    # Estado
    activo = models.BooleanField(default=True)
    publicado = models.BooleanField(default=False, help_text="Si está visible para los estudiantes")
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'evaluaciones'
        verbose_name = 'Evaluación'
        verbose_name_plural = 'Evaluaciones'
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"{self.titulo} - {self.materia.nombre} ({self.tipo_evaluacion})"

    @property
    def esta_vencido(self):
        from django.utils import timezone
        return timezone.now().date() > self.fecha_entrega

    @property
    def puede_entregar_tardio(self):
        from django.utils import timezone
        if not self.permite_entrega_tardia or not self.fecha_limite:
            return False
        return timezone.now().date() <= self.fecha_limite

class Calificacion(models.Model):
    """
    Almacena las calificaciones de los estudiantes en las evaluaciones.
    """
    evaluacion = models.ForeignKey(Evaluacion, on_delete=models.CASCADE, related_name='calificaciones')
    estudiante = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE)
    
    # Calificación
    nota = models.DecimalField(max_digits=5, decimal_places=2)
    nota_sobre = models.DecimalField(max_digits=5, decimal_places=2, help_text="Nota máxima posible")
    
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
        unique_together = ['evaluacion', 'estudiante']

    def __str__(self):
        return f"{self.estudiante.nombre} - {self.evaluacion.titulo}: {self.nota}/{self.nota_sobre}"

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
        return self.nota_final >= self.evaluacion.nota_minima_aprobacion

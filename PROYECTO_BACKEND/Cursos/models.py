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

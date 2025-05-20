from django.db import models

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
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='materias')

    class Meta:
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'

    def __str__(self):
        return self.nombre

class Notas(models.Model):
    id = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=4, decimal_places=2)
    concepto = models.CharField(max_length=100, null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    estudiante = models.ForeignKey('Usuarios.Estudiante', on_delete=models.CASCADE, related_name='notas')
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
    estudiante = models.ForeignKey('Usuarios.Estudiante', on_delete=models.CASCADE, related_name='boletines')
    notas = models.ManyToManyField(Notas, related_name='boletines')

    class Meta:
        verbose_name = 'Boletín'
        verbose_name_plural = 'Boletines'

    def __str__(self):
        return f"Boletín {self.id}: {self.estudiante} - {self.periodo}"

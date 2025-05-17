from django.db import models

class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50)
    usuarios = models.ManyToManyField('Usuarios.Usuario', related_name='roles')

    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre

class Privilegio(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    roles = models.ManyToManyField(Rol, related_name='privilegios')

    class Meta:
        verbose_name = 'Privilegio'
        verbose_name_plural = 'Privilegios'

    def __str__(self):
        return self.nombre

class Permiso(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    privilegios = models.ManyToManyField(Privilegio, related_name='permisos')

    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'

    def __str__(self):
        return self.nombre

class Notificacion(models.Model):
    id = models.AutoField(primary_key=True)
    tipo = models.CharField(max_length=50)
    mensaje = models.TextField()
    fecha = models.DateField(auto_now_add=True)
    estado = models.IntegerField(default=0)  # 0: No leída, 1: Leída, 2: Archivada
    usuario = models.ForeignKey('Usuarios.Usuario', on_delete=models.CASCADE, related_name='notificaciones')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'

    def __str__(self):
        return f"{self.tipo}: {self.mensaje[:30]}..."
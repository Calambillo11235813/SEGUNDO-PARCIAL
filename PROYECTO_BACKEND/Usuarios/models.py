from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UsuarioManager(BaseUserManager):
    def create_user(self, id, nombre, apellido, password=None, **extra_fields):
        if not id:
            raise ValueError('El ID es obligatorio')
        user = self.model(id=id, nombre=nombre, apellido=apellido, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, id, nombre, apellido, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(id, nombre, apellido, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.IntegerField(null=True, blank=True)
    contrasena = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UsuarioManager()
    
    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre

    def set_password(self, raw_password):
        from django.contrib.auth.hashers import make_password
        self.contrasena = make_password(raw_password)  # En un sistema real, deberías hashear la contraseña

class Profesor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    materias = models.ManyToManyField('Cursos.Materia', related_name='profesores')

    class Meta:
        verbose_name = 'Profesor'
        verbose_name_plural = 'Profesores'

    def __str__(self):
        return f"Profesor: {self.usuario.nombre} {self.usuario.apellido}"

class Estudiante(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    curso = models.ForeignKey('Cursos.Curso', on_delete=models.SET_NULL, null=True, related_name='estudiantes')

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"Estudiante: {self.usuario.nombre} {self.usuario.apellido}"

class Tutor(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)
    estudiantes = models.ManyToManyField(Estudiante, related_name='tutores')

    class Meta:
        verbose_name = 'Tutor'
        verbose_name_plural = 'Tutores'

    def __str__(self):
        return f"Tutor: {self.usuario.nombre} {self.usuario.apellido}"

class Administrativo(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, primary_key=True)

    class Meta:
        verbose_name = 'Administrativo'
        verbose_name_plural = 'Administrativos'

    def __str__(self):
        return f"Admin: {self.usuario.nombre} {self.usuario.apellido}"

class Bitacora(models.Model):
    id = models.AutoField(primary_key=True)
    fecha = models.DateField(auto_now_add=True)
    hora = models.TimeField(auto_now_add=True)
    accion = models.TextField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='bitacoras')

    class Meta:
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'

    def __str__(self):
        return f"Bitácora {self.id}: {self.accion} por {self.usuario.nombre}"

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from Permisos.models import Rol
import random
import string

class UsuarioManager(BaseUserManager):
    def create_user(self, nombre, apellido, codigo=None, password=None, **extra_fields):
        """
        Crea y guarda un Usuario con el nombre, apellido y contraseña dados.
        """
        if not nombre:
            raise ValueError('El nombre es obligatorio')
        if not apellido:
            raise ValueError('El apellido es obligatorio')
        
        # Si no se proporciona un código, generar uno aleatorio
        if codigo is None:
            # Generar código único
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        # Crear el usuario con los datos proporcionados
        user = self.model(
            nombre=nombre,
            apellido=apellido,
            codigo=codigo,
            **extra_fields
        )
        
        if password:
            user.set_password(password)  # Esto llama al método correcto de Django
        else:
            user.set_unusable_password()  # Si no hay contraseña, establecer una no usable
        
        user.save(using=self._db)
        return user
    
    def create_superuser(self, nombre, apellido, codigo=None, password=None, **extra_fields):
        """Crea y guarda un superusuario"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        return self.create_user(nombre, apellido, codigo, password, **extra_fields)

class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True, verbose_name='Código de acceso')
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    telefono = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    # Cambiar la relación a ForeignKey (un usuario, un rol)
    rol = models.ForeignKey(
        Rol, 
        on_delete=models.SET_NULL,  # Si se borra un rol, los usuarios no serán eliminados
        null=True,  # Permitir usuarios sin rol
        blank=True,
        related_name='usuarios_rol'  # Nombre diferenciado para la relación inversa
    )
    
    # Añadir este campo
    curso = models.ForeignKey('Cursos.Curso', on_delete=models.SET_NULL, 
                              null=True, blank=True, related_name='estudiantes_usuarios',
                              help_text="Curso al que pertenece el estudiante (solo para estudiantes)")
    


    objects = UsuarioManager()
    
    USERNAME_FIELD = 'codigo'  # Los usuarios iniciarán sesión con su código
    REQUIRED_FIELDS = ['nombre', 'apellido']

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        db_table = 'usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.rol.nombre}"

    def get_full_name(self):
        return f"{self.nombre} {self.apellido}"

    def get_short_name(self):
        return self.nombre

    def set_password(self, raw_password):
        """
        Usa el método set_password de Django para establecer la contraseña.
        """
        super().set_password(raw_password)

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

    class Meta:
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"Estudiante: {self.usuario.nombre} {self.usuario.apellido}"

    # Método de conveniencia para acceder al curso
    @property
    def curso(self):
        return self.usuario.curso

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

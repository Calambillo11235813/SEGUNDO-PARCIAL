class Usuario {
  final int id;
  final String nombre;
  final String apellido;
  final String codigo;
  final Map<String, dynamic>? rol;

  Usuario({
    required this.id,
    required this.nombre,
    required this.apellido,
    required this.codigo,
    this.rol,
  });

  // Propiedad para obtener el nombre completo
  String get nombreCompleto => '$nombre $apellido';

  // Métodos para verificar el rol - más defensivos
  bool get isEstudiante {
    if (rol == null) return false;
    final rolNombre = rol!['nombre']?.toString().toLowerCase();
    return rolNombre == 'estudiante';
  }

  bool get isProfesor {
    if (rol == null) return false;
    final rolNombre = rol!['nombre']?.toString().toLowerCase();
    return rolNombre == 'profesor';
  }

  // Método para obtener el nombre del rol de forma segura
  String get rolNombre {
    if (rol == null || rol!['nombre'] == null) return 'Sin rol';
    return rol!['nombre'].toString();
  }

  // Añadir este getter a la clase Usuario
  bool get isTutor => rol != null && rol!['nombre'] == 'Tutor';

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'] ?? 0,
      nombre: json['nombre'] ?? '',
      apellido: json['apellido'] ?? '',
      codigo: json['codigo'] ?? '',
      rol: json['rol'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'nombre': nombre,
      'apellido': apellido,
      'codigo': codigo,
      'rol': rol,
    };
  }

  @override
  String toString() {
    return '$nombreCompleto - $rolNombre';
  }
}

extension UsuarioExtensions on Usuario {
  /// Obtiene el nombre completo del usuario
  String get nombreCompleto => '$nombre $apellido';

  /// Obtiene las iniciales del usuario
  String get iniciales {
    final nombreInicial = nombre.isNotEmpty ? nombre[0].toUpperCase() : '';
    final apellidoInicial =
        apellido.isNotEmpty ? apellido[0].toUpperCase() : '';
    return '$nombreInicial$apellidoInicial'.isEmpty
        ? 'U'
        : '$nombreInicial$apellidoInicial';
  }

  /// Obtiene el nombre del rol de forma segura
  String get rolNombre => rol?['nombre'] ?? 'Sin rol';

  /// Verifica si el usuario es estudiante
  bool get isEstudiante => rolNombre == 'Estudiante';

  /// Verifica si el usuario es tutor
  bool get isTutor => rolNombre == 'Tutor';

  /// Verifica si el usuario es profesor
  bool get isProfesor => rolNombre == 'Profesor';

  /// Verifica si el usuario tiene un rol específico
  bool hasRole(String roleName) => rolNombre == roleName;
}

// Extension para manejo de nullable Usuario
extension UsuarioNullableExtensions on Usuario? {
  /// Obtiene el nombre completo de forma segura
  String get safeNombreCompleto {
    if (this == null) return 'Usuario';
    return this!.nombreCompleto;
  }

  /// Obtiene las iniciales de forma segura
  String get safeIniciales {
    if (this == null) return 'U';
    return this!.iniciales;
  }

  /// Obtiene el código de forma segura
  String get safeCodigo {
    if (this == null) return 'Sin código';
    return this!.codigo;
  }

  /// Verifica si el usuario tiene un rol específico de forma segura
  bool hasSafeRole(String roleName) {
    if (this == null) return false;
    return this!.hasRole(roleName);
  }
}

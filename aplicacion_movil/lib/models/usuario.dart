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

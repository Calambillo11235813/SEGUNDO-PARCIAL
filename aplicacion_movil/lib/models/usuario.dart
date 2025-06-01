class Usuario {
  final int id;
  final String nombre;
  final String apellido;
  final String codigo;
  final Map<String, dynamic>? rol;
  final Map<String, dynamic>? curso;

  Usuario({
    required this.id,
    required this.nombre,
    required this.apellido,
    required this.codigo,
    this.rol,
    this.curso,
  });

  factory Usuario.fromJson(Map<String, dynamic> json) {
    return Usuario(
      id: json['id'],
      nombre: json['nombre'],
      apellido: json['apellido'],
      codigo: json['codigo'],
      rol: json['rol'],
      curso: json['curso'],
    );
  }

  String get nombreCompleto => '$nombre $apellido';

  bool get isEstudiante => rol != null && rol!['nombre'] == 'Estudiante';
  bool get isProfesor => rol != null && rol!['nombre'] == 'Profesor';
  bool get isAdministrador => rol != null && rol!['nombre'] == 'Administrador';
}

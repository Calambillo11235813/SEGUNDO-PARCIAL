class ApiConfig {
  // Cambia esto a la dirección IP de tu máquina si estás usando un emulador
  // Para Android emulator: usar 10.0.2.2 en lugar de localhost
  // Para dispositivos físicos: usar tu dirección IP local (ej: 192.168.1.5)
  static const String baseUrl = 'http://192.168.0.6:8000/api';

  // Auth endpoints
  static const String loginEndpoint = '$baseUrl/usuarios/auth/login/';
  static const String registerEndpoint = '$baseUrl/usuarios/auth/register/';

  // Usuarios endpoints
  static const String usuariosEndpoint = '$baseUrl/usuarios/';
  static const String estudiantesEndpoint = '$baseUrl/usuarios/estudiantes/';
  static const String profesoresEndpoint = '$baseUrl/usuarios/profesores/';

  // Cursos endpoints
  static const String cursosEndpoint = '$baseUrl/cursos/';
  static const String materiasEndpoint = '$baseUrl/cursos/materias/';
  static const String trimestreEndpoint = '$baseUrl/cursos/trimestres/';
  static const String evaluacionesEndpoint = '$baseUrl/cursos/evaluaciones/';
  static const String calificacionesEndpoint =
      '$baseUrl/cursos/calificaciones/';
}

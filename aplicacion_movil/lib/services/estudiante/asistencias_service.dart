import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';

class AsistenciasService {
  static Future<List<dynamic>> obtenerAsistenciasPorEstudiante(
    String estudianteId, {
    String? materiaId,
    String? fechaInicio,
    String? fechaFin,
  }) async {
    try {
      final token = await AuthService.getToken();

      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Construir URL con parámetros opcionales
      String url =
          '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/asistencias/';

      // Añadir parámetros de consulta si existen
      final queryParams = <String>[];
      if (materiaId != null) {
        queryParams.add('materia_id=$materiaId');
      }
      if (fechaInicio != null) {
        queryParams.add('fecha_inicio=$fechaInicio');
      }
      if (fechaFin != null) {
        queryParams.add('fecha_fin=$fechaFin');
      }

      if (queryParams.isNotEmpty) {
        url += '?${queryParams.join('&')}';
      }

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['error'] ?? 'Error al obtener asistencias');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';

class EvaluacionesService {
  static Future<List<dynamic>> obtenerEvaluacionesPorEstudiante(
    String estudianteId, {
    String? materiaId,
    String? trimestreId,
  }) async {
    try {
      final token = await AuthService.getToken();

      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Construir URL con parámetros opcionales
      String url =
          '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/evaluaciones/';

      // Añadir parámetros de consulta si existen
      final queryParams = <String>[];
      if (materiaId != null) {
        queryParams.add('materia_id=$materiaId');
      }
      if (trimestreId != null) {
        queryParams.add('trimestre_id=$trimestreId');
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
        throw Exception(errorData['error'] ?? 'Error al obtener evaluaciones');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}

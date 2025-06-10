import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';
import '../../utils/logger.dart'; // Importar el logger

class MateriasService {
  static Future<Map<String, dynamic>> obtenerMateriasPorEstudiante(
    String estudianteId,
  ) async {
    try {
      final token = await AuthService.getToken();

      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final response = await http.get(
        Uri.parse(
          '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/curso-materias/',
        ),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        final errorData = jsonDecode(response.body);
        throw Exception(errorData['error'] ?? 'Error al obtener materias');
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }

  // NUEVA FUNCIÓN: Obtener tipos de evaluación por materia
  static Future<Map<String, dynamic>> obtenerTiposEvaluacionPorMateria(
    String materiaId, {
    int? anio, // Añadir parámetro opcional para año
  }) async {
    try {
      final token = await AuthService.getToken();
      String url =
          '${ApiConfig.baseUrl}/cursos/materias/$materiaId/tipos-evaluacion/';

      // Construir parámetros de consulta
      Map<String, String> queryParams = {};
      if (anio != null) {
        queryParams['anio'] = anio.toString();
      }

      final uri = Uri.parse(url).replace(queryParameters: queryParams);

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        AppLogger.e('Error al obtener tipos de evaluación', response.body);
        throw Exception('Error al obtener tipos de evaluación');
      }
    } catch (e) {
      AppLogger.e('Error en servicio de materias', e);
      rethrow;
    }
  }
}

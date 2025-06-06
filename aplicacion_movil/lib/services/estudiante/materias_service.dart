import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';

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
    int materiaId,
  ) async {
    try {
      final token = await AuthService.getToken();

      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final response = await http.get(
        Uri.parse(
          '${ApiConfig.baseUrl}/cursos/materias/$materiaId/tipos-evaluacion/',
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
        throw Exception(
          errorData['error'] ?? 'Error al obtener tipos de evaluación',
        );
      }
    } catch (e) {
      throw Exception('Error de conexión: $e');
    }
  }
}

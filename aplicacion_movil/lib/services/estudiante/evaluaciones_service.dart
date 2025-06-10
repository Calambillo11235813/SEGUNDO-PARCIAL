import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';
import '../../utils/logger.dart';

class EvaluacionesService {
  // Método actualizado con filtro por año
  static Future<List<dynamic>> obtenerEvaluacionesPorEstudiante(
    String estudianteId, {
    String? materiaId,
    int? anio,
  }) async {
    try {
      final token = await AuthService.getToken();

      // Restaurar la URL original usando el estudianteId dinámico
      String url =
          '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/evaluaciones/';

      // Restaurar los parámetros de consulta originales
      Map<String, String> queryParams = {};
      if (materiaId != null) {
        queryParams['materia_id'] = materiaId;
      }
      if (anio != null) {
        queryParams['anio'] = anio.toString();
      }

      final uri = Uri.parse(url).replace(queryParameters: queryParams);
      AppLogger.i("📡 Request URL: $uri");

      final response = await http.get(
        uri,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        AppLogger.i("📥 Evaluaciones recibidas: ${data.length}");

        // Revisar si hay evaluaciones con calificaciones
        int conCalificacion = 0;
        for (var eval in data) {
          if (eval['calificacion'] != null) {
            conCalificacion++;
            AppLogger.i(
              "✅ Evaluación con calificación: ID=${eval['id']}, Nota=${eval['calificacion']['nota']}",
            );
          }
        }
        AppLogger.i(
          "📊 Total evaluaciones con calificación: $conCalificacion/${data.length}",
        );

        return data;
      } else {
        AppLogger.w(
          "❌ Error en respuesta: ${response.statusCode} - ${response.body}",
        );
        throw Exception(
          'Error al obtener evaluaciones: ${response.statusCode}',
        );
      }
    } catch (e) {
      AppLogger.e("🔥 Exception en evaluaciones_service: $e");
      rethrow;
    }
  }
}

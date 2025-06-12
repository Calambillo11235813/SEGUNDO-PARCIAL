import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';

class PrediccionService {
  static Future<Map<String, dynamic>?> predecirRendimiento({
    required double promedioNotasAnterior,
    required double porcentajeAsistencia,
    required double promedioParticipaciones,
    required int materiasCursadas,
    required int evaluacionesCompletadas,
    String? estudianteCodigo, // Opcional
  }) async {
    final String? token = await AuthService.getToken();
    final url = Uri.parse('${ApiConfig.baseIaUrl}/predecir/');

    final Map<String, dynamic> body = {
      'promedio_notas_anterior': promedioNotasAnterior,
      'porcentaje_asistencia': porcentajeAsistencia,
      'promedio_participaciones': promedioParticipaciones,
      'materias_cursadas': materiasCursadas,
      'evaluaciones_completadas': evaluacionesCompletadas,
      if (estudianteCodigo != null) 'estudiante_codigo': estudianteCodigo,
    };

    try {
      final response = await http.post(
        url,
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
        body: json.encode(body),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        // Puedes manejar errores específicos aquí
        return null;
      }
    } catch (e) {
      // Manejo de error de red o parsing
      return null;
    }
  }
}

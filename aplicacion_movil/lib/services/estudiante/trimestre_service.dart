import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class TrimestreService {
  // NUEVO MÉTODO: Obtener trimestres por estudiante
  Future<List<dynamic>> obtenerTrimestresEstudiante(int estudianteId) async {
    try {
      // Verificar la URL base
      AppLogger.i('URL BASE: ${ApiConfig.baseUrl}');

      // Obtener token usando el método estático
      final token = await AuthService.getToken();
      AppLogger.d(
        'Token obtenido: ${token != null ? (token.length > 15 ? token.substring(0, 15) : token) : "No hay token"}...',
      );

      // Construir y loguear la URL
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/trimestres/',
      );
      AppLogger.i('⭐ Intentando acceder a URL: $url');

      // Loguear los headers para verificar
      final headers = {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      };
      AppLogger.d('Headers: $headers');

      // Realizar la solicitud HTTP
      final response = await http.get(url, headers: headers);

      // Loguear la respuesta
      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode != 200) {
        AppLogger.e(
          'Error en la respuesta: ${response.statusCode}',
          response.body,
        );
      } else {
        AppLogger.i('Respuesta recibida correctamente');
        AppLogger.d('Tamaño respuesta: ${response.body.length} bytes');
      }

      if (response.statusCode == 200) {
        final List<dynamic> resultado = jsonDecode(response.body);
        AppLogger.i(
          'Años académicos con trimestres obtenidos: ${resultado.length}',
        );

        // Los datos ya vienen estructurados por año desde el backend
        return resultado;
      } else {
        throw Exception(
          'Error al cargar trimestres del estudiante: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error obteniendo trimestres del estudiante', e, stackTrace);
      rethrow;
    }
  }

  // NUEVO MÉTODO: Obtener calificaciones por trimestre de un estudiante
  Future<Map<String, dynamic>> obtenerCalificacionesTrimestre(
    int estudianteId,
    int trimestreId,
  ) async {
    try {
      // Obtener token usando el método estático
      final token = await AuthService.getToken();

      // Construir la URL
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/trimestres/$trimestreId/calificaciones/',
      );
      AppLogger.i('⭐ Intentando acceder a URL: $url');

      // Realizar la solicitud HTTP
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      // Loguear la respuesta
      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode != 200) {
        AppLogger.e(
          'Error obteniendo calificaciones: ${response.statusCode}',
          response.body,
        );
        throw Exception(
          'Error al cargar calificaciones: ${response.statusCode}',
        );
      }

      // Convertir la respuesta a Map y devolverla
      final Map<String, dynamic> calificaciones = jsonDecode(response.body);
      AppLogger.i(
        'Calificaciones obtenidas para ${calificaciones['materias']?.length} materias',
      );

      return calificaciones;
    } catch (e, stackTrace) {
      AppLogger.e(
        'Error obteniendo calificaciones del trimestre',
        e,
        stackTrace,
      );
      rethrow;
    }
  }
}

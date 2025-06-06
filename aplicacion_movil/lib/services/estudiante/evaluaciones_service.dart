import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';
import '../../utils/logger.dart'; // Importar el logger

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

      // Usar logger en vez de print
      AppLogger.d('Realizando petición a: $url');

      final response = await http.get(
        Uri.parse(url),
        headers: {
          'Accept': 'application/json',
          'Authorization': 'Bearer $token',
        },
      );

      // Respuesta de depuración con logger
      AppLogger.i('Código de estado: ${response.statusCode}');
      AppLogger.d(
        'Primeros 100 caracteres de respuesta: ${response.body.length > 100 ? response.body.substring(0, 100) : response.body}',
      );

      if (response.statusCode == 200) {
        // Verificar que la respuesta parece JSON antes de decodificar
        if (response.body.trim().startsWith('{') ||
            response.body.trim().startsWith('[')) {
          return jsonDecode(response.body);
        } else {
          throw Exception('La respuesta no es un JSON válido');
        }
      } else {
        // Intentar decodificar solo si parece JSON
        if (response.body.trim().startsWith('{') ||
            response.body.trim().startsWith('[')) {
          try {
            final errorData = jsonDecode(response.body);
            throw Exception(
              errorData['error'] ?? 'Error al obtener evaluaciones',
            );
          } catch (e) {
            throw Exception(
              'Error de servidor (${response.statusCode}): Formato de respuesta inválido',
            );
          }
        } else {
          throw Exception(
            'Error de servidor (${response.statusCode}): No se recibió un JSON',
          );
        }
      }
    } catch (e) {
      // Al capturar excepciones, usa el logger
      if (e is FormatException) {
        AppLogger.e('Error de formato al procesar la respuesta', e);
        throw Exception(
          'Error de formato al procesar la respuesta: ${e.message}',
        );
      }
      AppLogger.e('Error de conexión', e);
      throw Exception('Error de conexión: $e');
    }
  }
}

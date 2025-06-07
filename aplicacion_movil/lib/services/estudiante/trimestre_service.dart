import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class TrimestreService {
  Future<Map<int, List<dynamic>>> obtenerAniosAcademicosTrimestres() async {
    try {
      // Verificar la URL base
      AppLogger.i('URL BASE: ${ApiConfig.baseUrl}');

      // Obtener token usando el método estático
      final token = await AuthService.getToken();
      AppLogger.d(
        'Token obtenido: ${token != null ? (token.length > 15 ? token.substring(0, 15) : token) : "No hay token"}...',
      ); // Solo mostrar parte por seguridad

      // Construir y loguear la URL
      final url = Uri.parse('${ApiConfig.baseUrl}/cursos/trimestres/');
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
        final List<dynamic> trimestres = jsonDecode(response.body);
        AppLogger.i('Trimestres obtenidos: ${trimestres.length}');

        // Agrupar trimestres por año académico
        final Map<int, List<dynamic>> aniosConTrimestres = {};

        for (var trimestre in trimestres) {
          final int anio = trimestre['año_academico'];
          if (!aniosConTrimestres.containsKey(anio)) {
            aniosConTrimestres[anio] = [];
          }
          aniosConTrimestres[anio]?.add(trimestre);
        }

        // Log de los años encontrados
        AppLogger.i(
          'Años académicos encontrados: ${aniosConTrimestres.keys.toList()}',
        );

        // Ordenar los años de más reciente a más antiguo
        final sortedMap = Map.fromEntries(
          aniosConTrimestres.entries.toList()
            ..sort((a, b) => b.key.compareTo(a.key)),
        );

        return sortedMap;
      } else {
        throw Exception('Error al cargar trimestres: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error obteniendo años académicos', e, stackTrace);
      rethrow;
    }
  }
}

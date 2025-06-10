import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class FiltrosTutorService {
  // Obtener años académicos disponibles
  static Future<List<String>> obtenerAniosAcademicos() async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final url = Uri.parse('${ApiConfig.baseUrl}/cursos/años-academicos/');
      AppLogger.i('⭐ Obteniendo años académicos disponibles: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final List<dynamic> anios = jsonDecode(response.body);
        final List<String> aniosString =
            anios.map((anio) => anio.toString()).toList();
        AppLogger.i('Años académicos obtenidos: ${aniosString.join(", ")}');
        return aniosString;
      } else {
        AppLogger.e(
          'Error obteniendo años académicos: ${response.statusCode}',
          response.body,
        );
        throw Exception(
          'Error al obtener años académicos: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerAniosAcademicos', e, stackTrace);
      rethrow;
    }
  }

  // Obtener trimestres por año académico
  static Future<List<Map<String, dynamic>>> obtenerTrimestresPorAnio(
    String anioAcademico,
  ) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/trimestres/?año_academico=$anioAcademico',
      );
      AppLogger.i('⭐ Obteniendo trimestres para el año $anioAcademico: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final List<dynamic> trimestres = jsonDecode(response.body);
        final List<Map<String, dynamic>> trimestresFormatted =
            trimestres.cast<Map<String, dynamic>>().toList();
        AppLogger.i('Trimestres obtenidos: ${trimestresFormatted.length}');
        return trimestresFormatted;
      } else {
        AppLogger.e(
          'Error obteniendo trimestres: ${response.statusCode}',
          response.body,
        );
        throw Exception('Error al obtener trimestres: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerTrimestresPorAnio', e, stackTrace);
      rethrow;
    }
  }

  // Obtener materias disponibles para un curso específico
  static Future<List<Map<String, dynamic>>> obtenerMateriasPorCurso(
    int cursoId,
  ) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/cursos/$cursoId/materias/',
      );
      AppLogger.i('⭐ Obteniendo materias para el curso $cursoId: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final List<dynamic> materias = jsonDecode(response.body);
        final List<Map<String, dynamic>> materiasFormatted =
            materias.cast<Map<String, dynamic>>().toList();
        AppLogger.i('Materias obtenidas: ${materiasFormatted.length}');
        return materiasFormatted;
      } else {
        AppLogger.e(
          'Error obteniendo materias: ${response.statusCode}',
          response.body,
        );
        throw Exception('Error al obtener materias: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerMateriasPorCurso', e, stackTrace);
      rethrow;
    }
  }
}

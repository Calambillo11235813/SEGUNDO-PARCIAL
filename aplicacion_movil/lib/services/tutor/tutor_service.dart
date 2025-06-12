import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class TutorService {
  // Obtener los estudiantes asignados a un tutor
  static Future<Map<String, dynamic>> obtenerEstudiantesTutor(
    int tutorId,
  ) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/tutores/$tutorId/estudiantes/',
      );
      AppLogger.i('⭐ Obteniendo estudiantes del tutor: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> resultado = jsonDecode(response.body);
        AppLogger.i(
          'Se encontraron ${resultado['total']} estudiantes para el tutor',
        );
        return resultado;
      } else {
        AppLogger.e(
          'Error obteniendo estudiantes del tutor: ${response.statusCode}',
          response.body,
        );
        throw Exception('Error al obtener estudiantes: ${response.statusCode}');
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerEstudiantesTutor', e, stackTrace);
      rethrow;
    }
  }

  // Obtener las calificaciones de todos los estudiantes asignados al tutor
  static Future<Map<String, dynamic>> obtenerCalificacionesEstudiantes(
    int tutorId, {
    int? trimestreId,
    int? materiaId,
    String? anioAcademico,
  }) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Construir URL con parámetros opcionales
      final queryParams = <String>[];
      if (trimestreId != null) {
        queryParams.add('trimestre_id=$trimestreId');
      }
      if (materiaId != null) {
        queryParams.add('materia_id=$materiaId');
      }
      if (anioAcademico != null) {
        queryParams.add('año_academico=$anioAcademico');
      }

      String urlString =
          '${ApiConfig.baseUrl}/cursos/tutores/$tutorId/calificaciones/';
      if (queryParams.isNotEmpty) {
        urlString += '?${queryParams.join('&')}';
      }

      final url = Uri.parse(urlString);
      AppLogger.i('⭐ Obteniendo calificaciones de estudiantes: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> resultado = jsonDecode(response.body);
        AppLogger.i(
          'Calificaciones obtenidas para ${resultado['total_estudiantes']} estudiantes',
        );
        return resultado;
      } else {
        AppLogger.e(
          'Error obteniendo calificaciones: ${response.statusCode}',
          response.body,
        );
        throw Exception(
          'Error al obtener calificaciones: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerCalificacionesEstudiantes', e, stackTrace);
      rethrow;
    }
  }

  // Obtener calificaciones detalladas de un estudiante específico
  static Future<Map<String, dynamic>> obtenerCalificacionesEstudianteDetalle(
    int tutorId,
    int estudianteId, {
    int? materiaId,
    int? trimestreId,
    int? tipoEvaluacionId,
    String? anioAcademico,
  }) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Construir URL con parámetros opcionales
      final queryParams = <String>[];
      if (materiaId != null) {
        queryParams.add('materia_id=$materiaId');
      }
      if (trimestreId != null) {
        queryParams.add('trimestre_id=$trimestreId');
      }
      if (tipoEvaluacionId != null) {
        queryParams.add('tipo_evaluacion_id=$tipoEvaluacionId');
      }
      if (anioAcademico != null) {
        queryParams.add('año_academico=$anioAcademico'); // AHORA FUNCIONAL
      }

      String urlString =
          '${ApiConfig.baseUrl}/cursos/tutores/$tutorId/estudiantes/$estudianteId/calificaciones/';
      if (queryParams.isNotEmpty) {
        urlString += '?${queryParams.join('&')}';
      }

      final url = Uri.parse(urlString);
      AppLogger.i('⭐ Obteniendo calificaciones detalladas: $url');

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      AppLogger.i('Código de respuesta: ${response.statusCode}');

      if (response.statusCode == 200) {
        final Map<String, dynamic> resultado = jsonDecode(response.body);

        // ✅ NORMALIZACIÓN: Mover materias a la raíz si están en estudiante
        if (resultado['estudiante'] != null &&
            resultado['estudiante']['materias'] != null &&
            resultado['materias'] == null) {
          AppLogger.d(
            'Normalizando estructura: moviendo materias de estudiante a raíz',
          );
          resultado['materias'] = resultado['estudiante']['materias'];

          // Opcional: limpiar materias del objeto estudiante para evitar duplicación
          final estudianteData = Map<String, dynamic>.from(
            resultado['estudiante'],
          );
          estudianteData.remove('materias');
          resultado['estudiante'] = estudianteData;
        }

        AppLogger.i(
          'Calificaciones detalladas obtenidas para el estudiante ${resultado['estudiante']['nombre']}',
        );

        // Validar estructura final
        if (resultado['materias'] == null) {
          AppLogger.w('No se encontraron materias después de la normalización');
          resultado['materias'] = <dynamic>[];
        }

        return resultado;
      } else {
        AppLogger.e(
          'Error obteniendo calificaciones detalladas: ${response.statusCode}',
          response.body,
        );
        throw Exception(
          'Error al obtener calificaciones detalladas: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e(
        'Error en obtenerCalificacionesEstudianteDetalle',
        e,
        stackTrace,
      );
      rethrow;
    }
  }
}

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class EstadisticasTutorService {
  // Obtener resumen de rendimiento de estudiantes asignados
  static Future<Map<String, dynamic>> obtenerResumenRendimiento(
    int tutorId, {
    String? anioAcademico,
    int? trimestreId,
  }) async {
    try {
      final token = await AuthService.getToken();
      if (token == null) {
        throw Exception('No hay sesión activa');
      }

      // Construir URL con parámetros opcionales
      final queryParams = <String>[];
      if (anioAcademico != null) {
        queryParams.add('año_academico=$anioAcademico');
      }
      if (trimestreId != null) {
        queryParams.add('trimestre_id=$trimestreId');
      }

      String urlString =
          '${ApiConfig.baseUrl}/cursos/tutores/$tutorId/estadisticas/rendimiento/';
      if (queryParams.isNotEmpty) {
        urlString += '?${queryParams.join('&')}';
      }

      final url = Uri.parse(urlString);
      AppLogger.i('⭐ Obteniendo resumen de rendimiento: $url');

      // Este endpoint es hipotético, asumimos que existe o deberíamos implementarlo
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
        AppLogger.i('Resumen de rendimiento obtenido');
        return resultado;
      } else {
        AppLogger.e(
          'Error obteniendo resumen de rendimiento: ${response.statusCode}',
          response.body,
        );
        throw Exception(
          'Error al obtener resumen de rendimiento: ${response.statusCode}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en obtenerResumenRendimiento', e, stackTrace);

      // Proporcionar datos de ejemplo si el endpoint no existe aún
      return {
        'total_estudiantes': 0,
        'aprobados': 0,
        'reprobados': 0,
        'sin_datos': 0,
        'promedio_general': 0.0,
        'mensaje': 'Funcionalidad en desarrollo. Error: $e',
      };
    }
  }

  // Método para procesar estadísticas localmente en caso de que no exista el endpoint
  static Map<String, dynamic> procesarEstadisticasLocalmente(
    Map<String, dynamic> datosCalificaciones,
  ) {
    try {
      AppLogger.i('Procesando estadísticas localmente');

      final estudiantes = datosCalificaciones['estudiantes'] as List<dynamic>;
      int totalEstudiantes = estudiantes.length;
      int aprobados = 0;
      int reprobados = 0;
      int sinDatos = 0;
      double sumaPromedios = 0.0;
      int estudiantesConPromedio = 0;

      for (var estudiante in estudiantes) {
        final materias = estudiante['materias'] as List<dynamic>;
        if (materias.isEmpty) {
          sinDatos++;
          continue;
        }

        bool estudianteAprobado = true;
        double sumaPromediosEstudiante = 0.0;
        int materiasConPromedio = 0;

        for (var materia in materias) {
          final trimestres = materia['trimestres'] as List<dynamic>;
          if (trimestres.isEmpty) continue;

          // Tomamos el primer trimestre (suponiendo que están ordenados por más reciente)
          final trimestre = trimestres[0];
          if (trimestre['promedio'] != null) {
            double promedio = trimestre['promedio'].toDouble();
            sumaPromediosEstudiante += promedio;
            materiasConPromedio++;

            if (trimestre['aprobado'] == false) {
              estudianteAprobado = false;
            }
          }
        }

        if (materiasConPromedio > 0) {
          double promedioEstudiante =
              sumaPromediosEstudiante / materiasConPromedio;
          sumaPromedios += promedioEstudiante;
          estudiantesConPromedio++;

          if (estudianteAprobado) {
            aprobados++;
          } else {
            reprobados++;
          }
        } else {
          sinDatos++;
        }
      }

      double promedioGeneral =
          estudiantesConPromedio > 0
              ? sumaPromedios / estudiantesConPromedio
              : 0.0;

      return {
        'total_estudiantes': totalEstudiantes,
        'aprobados': aprobados,
        'reprobados': reprobados,
        'sin_datos': sinDatos,
        'promedio_general': promedioGeneral,
        'calculado_localmente': true,
      };
    } catch (e, stackTrace) {
      AppLogger.e('Error al procesar estadísticas localmente', e, stackTrace);
      return {
        'error': 'No se pudieron procesar las estadísticas',
        'mensaje': e.toString(),
      };
    }
  }
}

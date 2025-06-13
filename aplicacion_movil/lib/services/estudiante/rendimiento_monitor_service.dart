import 'dart:convert';
import 'package:http/http.dart' as http;
import '../auth_service.dart';
import '../../config/api_config.dart';
import '../../utils/logger.dart';

class RendimientoMonitorService {
  static const double NOTA_MINIMA = 51.0; // Nota mínima de aprobación

  /// Verifica el rendimiento académico general del estudiante
  static Future<Map<String, dynamic>> verificarRendimientoGeneral(
    String estudianteId,
  ) async {
    try {
      final token = await AuthService.getToken();
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/estudiantes/$estudianteId/rendimiento/general',
      );

      AppLogger.i("📡 Verificando rendimiento general: $url");
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        AppLogger.d(
          "Datos de rendimiento recibidos: ${data.toString().substring(0, 100)}...",
        );

        // Analizar situación de riesgo
        final situacionRiesgo = _analizarSituacionRiesgo(data);
        return situacionRiesgo;
      } else {
        AppLogger.e(
          'Error obteniendo rendimiento: ${response.statusCode} - ${response.body}',
        );
        return {
          'error': true,
          'message': 'Error al obtener rendimiento: ${response.statusCode}',
        };
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en verificarRendimientoGeneral', e, stackTrace);
      return {'error': true, 'message': e.toString()};
    }
  }

  /// Verifica el rendimiento por materia específica
  static Future<Map<String, dynamic>> verificarRendimientoPorMateria(
    String estudianteId,
    String materiaId,
  ) async {
    try {
      final token = await AuthService.getToken();
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/estudiantes/$estudianteId/materias/$materiaId/rendimiento',
      );

      AppLogger.i("📡 Verificando rendimiento por materia: $url");
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return _analizarSituacionRiesgoMateria(data, materiaId);
      } else {
        AppLogger.e(
          'Error obteniendo rendimiento de materia: ${response.statusCode}',
        );
        return {
          'error': true,
          'message': 'Error al obtener rendimiento: ${response.statusCode}',
        };
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en verificarRendimientoPorMateria', e, stackTrace);
      return {'error': true, 'message': e.toString()};
    }
  }

  /// Verifica el rendimiento por trimestre
  static Future<Map<String, dynamic>> verificarRendimientoPorTrimestre(
    String estudianteId,
    int anio,
    int trimestre,
  ) async {
    try {
      final token = await AuthService.getToken();
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/estudiantes/$estudianteId/trimestres/$anio/$trimestre/rendimiento',
      );

      AppLogger.i("📡 Verificando rendimiento por trimestre: $url");
      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return _analizarSituacionRiesgoTrimestre(data, anio, trimestre);
      } else {
        AppLogger.e(
          'Error obteniendo rendimiento de trimestre: ${response.statusCode}',
        );
        return {
          'error': true,
          'message': 'Error al obtener rendimiento: ${response.statusCode}',
        };
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error en verificarRendimientoPorTrimestre', e, stackTrace);
      return {'error': true, 'message': e.toString()};
    }
  }

  /// Analiza los datos de rendimiento general para detectar situaciones de riesgo
  static Map<String, dynamic> _analizarSituacionRiesgo(
    Map<String, dynamic> datos,
  ) {
    double promedioGeneral = datos['promedio_general'] ?? 0.0;
    List<dynamic> materiasBajoRendimiento = [];

    // Verificar materias con bajo rendimiento
    if (datos['materias'] != null) {
      for (var materia in datos['materias']) {
        double promedio = materia['promedio'] ?? 0.0;
        if (promedio < NOTA_MINIMA) {
          materiasBajoRendimiento.add({
            'id': materia['id'],
            'nombre': materia['nombre'],
            'promedio': promedio,
            'diferencia': NOTA_MINIMA - promedio,
          });
        }
      }
    }

    bool enRiesgo =
        promedioGeneral < NOTA_MINIMA || materiasBajoRendimiento.isNotEmpty;

    return {
      'en_riesgo': enRiesgo,
      'promedio_general': promedioGeneral,
      'materias_riesgo': materiasBajoRendimiento,
      'materias_riesgo_count': materiasBajoRendimiento.length,
      'mensaje':
          enRiesgo
              ? 'Tu rendimiento académico está en riesgo. Tienes ${materiasBajoRendimiento.length} materia(s) por debajo del mínimo.'
              : 'Tu rendimiento académico es satisfactorio.',
    };
  }

  /// Analiza los datos de rendimiento de una materia específica
  static Map<String, dynamic> _analizarSituacionRiesgoMateria(
    Map<String, dynamic> datos,
    String materiaId,
  ) {
    double promedio = datos['promedio'] ?? 0.0;
    String nombreMateria = datos['nombre'] ?? 'Materia';
    List<dynamic> evaluacionesBajas = [];

    // Verificar evaluaciones con bajo rendimiento
    if (datos['evaluaciones'] != null) {
      for (var eval in datos['evaluaciones']) {
        double nota = eval['calificacion'] ?? 0.0;
        if (nota < NOTA_MINIMA) {
          evaluacionesBajas.add({
            'id': eval['id'],
            'titulo': eval['titulo'],
            'calificacion': nota,
            'diferencia': NOTA_MINIMA - nota,
          });
        }
      }
    }

    bool enRiesgo = promedio < NOTA_MINIMA;

    return {
      'en_riesgo': enRiesgo,
      'materia_id': materiaId,
      'nombre_materia': nombreMateria,
      'promedio': promedio,
      'diferencia': enRiesgo ? NOTA_MINIMA - promedio : 0,
      'evaluaciones_bajas': evaluacionesBajas,
      'evaluaciones_bajas_count': evaluacionesBajas.length,
      'mensaje':
          enRiesgo
              ? 'Tu rendimiento en $nombreMateria está en riesgo. Promedio: $promedio'
              : 'Tu rendimiento en $nombreMateria es satisfactorio. Promedio: $promedio',
    };
  }

  /// Analiza los datos de rendimiento de un trimestre específico
  static Map<String, dynamic> _analizarSituacionRiesgoTrimestre(
    Map<String, dynamic> datos,
    int anio,
    int trimestre,
  ) {
    double promedioTrimestre = datos['promedio_trimestre'] ?? 0.0;
    List<dynamic> materiasBajoRendimiento = [];

    // Verificar materias con bajo rendimiento en el trimestre
    if (datos['materias'] != null) {
      for (var materia in datos['materias']) {
        double promedio = materia['promedio_trimestre'] ?? 0.0;
        if (promedio < NOTA_MINIMA) {
          materiasBajoRendimiento.add({
            'id': materia['id'],
            'nombre': materia['nombre'],
            'promedio': promedio,
            'diferencia': NOTA_MINIMA - promedio,
          });
        }
      }
    }

    bool enRiesgo =
        promedioTrimestre < NOTA_MINIMA || materiasBajoRendimiento.isNotEmpty;

    return {
      'en_riesgo': enRiesgo,
      'anio': anio,
      'trimestre': trimestre,
      'promedio_trimestre': promedioTrimestre,
      'materias_riesgo': materiasBajoRendimiento,
      'materias_riesgo_count': materiasBajoRendimiento.length,
      'mensaje':
          enRiesgo
              ? 'Tu rendimiento en el trimestre $trimestre de $anio está en riesgo. Tienes ${materiasBajoRendimiento.length} materia(s) por debajo del mínimo.'
              : 'Tu rendimiento en el trimestre $trimestre de $anio es satisfactorio.',
    };
  }
}

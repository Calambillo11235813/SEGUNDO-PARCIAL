import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart';
import '../auth_service.dart';
import '../../utils/logger.dart';

class PrediccionService {
  static Future<Map<String, dynamic>> predecirRendimiento(
    Map<String, dynamic> datos,
  ) async {
    try {
      final token = await AuthService.getToken();

      // Usar la URL desde la configuración
      String url = ApiConfig.predecirRendimientoEndpoint;

      AppLogger.i("📊 URL para predicción: $url");
      AppLogger.i("📊 Enviando datos para predicción: $datos");

      final response = await http.post(
        Uri.parse(url),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode(datos),
      );

      if (response.statusCode == 200) {
        final resultado = jsonDecode(response.body);
        AppLogger.i("✅ Predicción exitosa: $resultado");
        return resultado;
      } else {
        AppLogger.e(
          "❌ Error en predicción: ${response.statusCode} - ${response.body}",
        );
        throw Exception(
          'Error al predecir rendimiento: ${response.statusCode}',
        );
      }
    } catch (e) {
      AppLogger.e("🔥 Exception en prediccion_service: $e");
      rethrow;
    }
  }

  static Map<String, dynamic> prepararDatosPrediccion(
    List<dynamic> evaluaciones,
  ) {
    // Valores por defecto
    Map<String, dynamic> datos = {
      "parcial1": 0.0, "parcial2": 0.0, "parcial3": 0.0,
      "practico1": 0.0, "practico2": 0.0, "practico3": 0.0,
      "practico4": 0.0, "practico5": 0.0, "practico6": 0.0,
      "participacion1": 0.0, "participacion2": 0.0,
      "participacion3": 0.0, "participacion4": 0.0,
      "asistencias": 95.0, // Valor por defecto para asistencia
    };

    // Clasificar evaluaciones por tipo
    List<Map<String, dynamic>> parciales = [];
    List<Map<String, dynamic>> practicos = [];
    List<Map<String, dynamic>> participaciones = [];

    for (var eval in evaluaciones) {
      if (eval['calificacion'] != null) {
        String tipoEvaluacionNombre = eval['tipo_evaluacion']?['nombre'] ?? '';
        double nota =
            double.tryParse(eval['calificacion']['nota'].toString()) ?? 0.0;

        // Clasificar según tipo
        if (tipoEvaluacionNombre == 'EXAMEN') {
          parciales.add({'nota': nota, 'titulo': eval['titulo']});
        } else if (tipoEvaluacionNombre == 'TRABAJO') {
          practicos.add({'nota': nota, 'titulo': eval['titulo']});
        } else if (tipoEvaluacionNombre == 'PARTICIPACION') {
          participaciones.add({'nota': nota, 'titulo': eval['titulo']});
        }
      }
    }

    // Asignar notas a los campos correspondientes
    for (int i = 0; i < parciales.length && i < 3; i++) {
      datos["parcial${i + 1}"] = parciales[i]['nota'];
    }

    for (int i = 0; i < practicos.length && i < 6; i++) {
      datos["practico${i + 1}"] = practicos[i]['nota'];
    }

    for (int i = 0; i < participaciones.length && i < 4; i++) {
      datos["participacion${i + 1}"] = participaciones[i]['nota'];
    }

    return datos;
  }
}

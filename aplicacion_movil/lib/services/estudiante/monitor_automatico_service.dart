import 'dart:async';
import '../../utils/logger.dart';
import '../../config/api_config.dart';
import '../auth_service.dart';
import '../notificaciones_service.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class MonitorAutomaticoService {
  static Timer? _timer;
  // Cambiar de 120 minutos a 2 minutos para pruebas
  static const int _intervalMinutos = 2; // Cambiado de 120 a 2 para pruebas
  static bool _isInitialized = false;
  // Eliminar el registro de alertas o resetearlas en cada verificación
  static final Map<String, bool> _alertasEnviadas = {};

  // Nota mínima de aprobación (podría venir de configuración)
  static const double notaMinima = 51.0;

  static void iniciar() {
    if (_isInitialized) return;

    AppLogger.i(
      '🔔 Iniciando servicio de monitoreo automático (MODO PRUEBA: 2 MINUTOS)',
    );
    _isInitialized = true;

    // Primera ejecución inmediata
    verificarRendimiento();

    // Programar ejecuciones periódicas cada 2 minutos
    _timer = Timer.periodic(
      Duration(minutes: _intervalMinutos),
      (_) => verificarRendimiento(),
    );
  }

  static void detener() {
    _timer?.cancel();
    _timer = null;
    _isInitialized = false;
    AppLogger.i('⏹️ Servicio de monitoreo detenido');
  }

  static Future<void> verificarRendimiento() async {
    try {
      AppLogger.i(
        '🔄 Verificando rendimiento académico del estudiante (MODO PRUEBA)',
      );

      // Limpiar alertas anteriores para permitir enviar nuevas alertas en cada verificación
      _alertasEnviadas.clear();

      final token = await AuthService.getToken();
      final userId = await AuthService.getCurrentUserId();

      if (token == null || userId == null) {
        AppLogger.w('❌ No hay sesión activa para verificar rendimiento');
        return;
      }

      // Obtener datos de rendimiento del estudiante
      final rendimiento = await _obtenerRendimientoActual(userId, token);

      // Verificar materias en riesgo
      _verificarMateriasEnRiesgo(rendimiento);

      AppLogger.i('✅ Verificación de rendimiento completada');
    } catch (e, stackTrace) {
      AppLogger.e('❌ Error al verificar rendimiento', e, stackTrace);
    }
  }

  static Future<Map<String, dynamic>> _obtenerRendimientoActual(
    int userId,
    String token,
  ) async {
    final url = Uri.parse(
      '${ApiConfig.baseUrl}/cursos/estudiantes/$userId/rendimiento-actual/',
    );

    final response = await http.get(
      url,
      headers: {
        'Authorization': 'Bearer $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Error al obtener rendimiento: ${response.statusCode}');
    }

    return jsonDecode(response.body);
  }

  static void _verificarMateriasEnRiesgo(Map<String, dynamic> rendimiento) {
    final materias = rendimiento['materias'] as List<dynamic>;
    final nombreEstudiante = rendimiento['estudiante']['nombre'];

    for (var materia in materias) {
      final nombreMateria = materia['nombre'] as String;
      final promedioActual = materia['promedio_actual'] as double?;
      final materiaCodigo = materia['codigo'] as String;

      // Si no hay promedio, no podemos evaluar
      if (promedioActual == null) continue;

      // Verificar si está en riesgo (por debajo de la nota mínima)
      if (promedioActual < notaMinima) {
        _enviarAlertaRendimiento(
          nombreEstudiante,
          nombreMateria,
          materiaCodigo,
          promedioActual,
        );
      }
    }

    // SOLO PARA PRUEBAS: Añadir una alerta de prueba para asegurar que siempre recibamos algo
    _enviarAlertaPrueba();
  }

  static void _enviarAlertaRendimiento(
    String nombreEstudiante,
    String nombreMateria,
    String materiaCodigo,
    double promedio,
  ) {
    // Clave única para esta alerta
    final alertaKey = '$materiaCodigo-${DateTime.now().millisecondsSinceEpoch}';

    // Para pruebas rápidas: no filtrar alertas duplicadas
    // if (_alertasEnviadas[alertaKey] == true) return;

    // Registrar que se ha enviado la alerta
    _alertasEnviadas[alertaKey] = true;

    AppLogger.i(
      '📊 Enviando alerta de rendimiento para $nombreMateria ($promedio)',
    );

    // Enviar notificación usando el servicio de notificaciones
    NotificacionesService.mostrarNotificacion(
      titulo: '⚠️ Alerta de rendimiento académico',
      cuerpo:
          'Tu promedio en $nombreMateria es $promedio, por debajo del mínimo aprobatorio.',
      payload: {'tipo': 'rendimiento', 'materia_codigo': materiaCodigo},
    );
  }

  // SOLO PARA PRUEBAS: Método para enviar siempre una alerta de prueba
  static void _enviarAlertaPrueba() {
    final timestamp = DateTime.now().toString();

    AppLogger.i('🧪 Enviando notificación de prueba: $timestamp');

    NotificacionesService.mostrarNotificacion(
      titulo: '🧪 Prueba de monitoreo automático',
      cuerpo:
          'Esta es una notificación de prueba generada a las ${timestamp.substring(11, 19)}',
      payload: {'tipo': 'prueba', 'timestamp': timestamp},
    );
  }
}

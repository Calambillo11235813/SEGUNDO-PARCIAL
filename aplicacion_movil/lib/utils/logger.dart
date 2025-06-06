import 'package:logger/logger.dart';

class AppLogger {
  static final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount:
          2, // Número de métodos de la pila de llamadas que se mostrarán
      errorMethodCount: 8, // Número de métodos para errores
      lineLength: 120, // Ancho de la línea de salida
      colors: true, // Colorear la salida
      printEmojis: true, // Mostrar emojis
      // printTime: true, // DEPRECATED: Ya no se usa
      // Usar dateTimeFormat en su lugar:
      dateTimeFormat: DateTimeFormat.onlyTimeAndSinceStart,
    ),
    level: Level.debug, // Nivel mínimo de log a mostrar (ajustable)
  );

  // Diferentes niveles de registro

  // Reemplazo de v() (verbose) por t() (trace)
  static void t(dynamic message) {
    _logger.t(message);
  }

  static void d(dynamic message) {
    _logger.d(message);
  }

  static void i(dynamic message) {
    _logger.i(message);
  }

  static void w(dynamic message) {
    _logger.w(message);
  }

  static void e(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    // Para errores, mantenemos capacidad de incluir error y stackTrace
    if (error != null) {
      _logger.e(
        '$message\nError: $error${stackTrace != null ? '\nStack: $stackTrace' : ''}',
      );
    } else {
      _logger.e(message);
    }
  }

  // Reemplazo de wtf() por f() (fatal)
  static void f(dynamic message, [dynamic error, StackTrace? stackTrace]) {
    // Para errores fatales, mantenemos capacidad de incluir error y stackTrace
    if (error != null) {
      _logger.f(
        '$message\nError: $error${stackTrace != null ? '\nStack: $stackTrace' : ''}',
      );
    } else {
      _logger.f(message);
    }
  }
}

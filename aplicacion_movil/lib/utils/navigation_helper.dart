import 'package:flutter/material.dart';
import 'logger.dart'; // Import del logger personalizado

class NavigationHelper {
  /// Obtiene argumentos de navegación de forma segura
  static Map<String, dynamic>? getSafeArguments(BuildContext context) {
    try {
      final route = ModalRoute.of(context);
      if (route?.settings.arguments == null) {
        return null;
      }

      final arguments = route!.settings.arguments;
      if (arguments is Map<String, dynamic>) {
        return arguments;
      }

      return null;
    } catch (e) {
      AppLogger.e("Error obteniendo argumentos de navegación", e);
      return null;
    }
  }

  /// Navega de forma segura con argumentos
  static Future<void> navigateTo(
    BuildContext context,
    String routeName, {
    Map<String, dynamic>? arguments,
  }) async {
    try {
      await Navigator.pushNamed(context, routeName, arguments: arguments);
    } catch (e) {
      AppLogger.e("Error en navegación a $routeName", e);
      // Mostrar error al usuario
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error de navegación: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Navega reemplazando la ruta actual
  static Future<void> navigateAndReplace(
    BuildContext context,
    String routeName, {
    Map<String, dynamic>? arguments,
  }) async {
    try {
      await Navigator.pushReplacementNamed(
        context,
        routeName,
        arguments: arguments,
      );
    } catch (e) {
      AppLogger.e("Error en navegación de reemplazo a $routeName", e);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error de navegación: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Cierra todas las rutas y navega a una nueva
  static Future<void> navigateAndClearStack(
    BuildContext context,
    String routeName, {
    Map<String, dynamic>? arguments,
  }) async {
    try {
      await Navigator.pushNamedAndRemoveUntil(
        context,
        routeName,
        (route) => false,
        arguments: arguments,
      );
    } catch (e) {
      AppLogger.e("Error limpiando stack de navegación", e);
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Error de navegación: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    }
  }

  /// Valida si una ruta puede ser navegada
  static bool canNavigate(BuildContext context, String routeName) {
    try {
      final route = ModalRoute.of(context);
      return route?.settings.name != routeName;
    } catch (e) {
      // ✅ CORRECCIÓN: Usar solo el mensaje, o concatenar la excepción
      AppLogger.w("Error validando navegación a $routeName: $e");
      return true;
    }
  }
}

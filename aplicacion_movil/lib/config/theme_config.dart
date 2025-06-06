import 'package:flutter/material.dart';

class AppTheme {
  // Colores principales
  static const Color primaryColor = Color(0xFF673AB7); // Deep Purple 500
  static const Color primaryColorLight = Color(0xFFD1C4E9); // Deep Purple 100
  static const Color primaryColorDark = Color(0xFF512DA8); // Deep Purple 700
  static const Color accentColor = Color(0xFF009688); // Teal 500

  // Colores secundarios para diferentes funcionalidades
  static const Color calificacionesColor = Color(0xFF7E57C2); // Deep Purple 400
  static const Color materiasColor = Color(0xFF00897B); // Teal 600
  static const Color asistenciaColor = Color(0xFFFF9800); // Orange 500
  static const Color rendimientoColor = Color(0xFFAB47BC); // Purple 400

  // Colores para estados
  static const Color successColor = Color(0xFF4CAF50); // Green 500
  static const Color warningColor = Color(0xFFFF9800); // Orange 500
  static const Color errorColor = Color(0xFFF44336); // Red 500
  static const Color infoColor = Color(0xFF2196F3); // Blue 500

  // Método para obtener un MaterialColor a partir de un Color
  static MaterialColor createMaterialColor(Color color) {
    List strengths = <double>[.05];
    Map<int, Color> swatch = {};
    // CORRECCIÓN: Convertir explícitamente double a int
    final int r = (color.r * 255).round();
    final int g = (color.g * 255).round();
    final int b = (color.b * 255).round();

    for (int i = 1; i < 10; i++) {
      strengths.add(0.1 * i);
    }
    for (var strength in strengths) {
      final double ds = 0.5 - strength;
      swatch[(strength * 1000).round()] = Color.fromRGBO(
        r + ((ds < 0 ? r : (255 - r)) * ds).round(),
        g + ((ds < 0 ? g : (255 - g)) * ds).round(),
        b + ((ds < 0 ? b : (255 - b)) * ds).round(),
        1,
      );
    }
    return MaterialColor(color.value, swatch);
  }

  // Define el tema claro de la aplicación
  static ThemeData lightTheme = ThemeData(
    primarySwatch: createMaterialColor(primaryColor),
    primaryColor: primaryColor,
    colorScheme: ColorScheme.light(
      primary: primaryColor,
      secondary: accentColor,
      error: errorColor,
    ),
    appBarTheme: const AppBarTheme(
      color: primaryColor,
      elevation: 0,
      iconTheme: IconThemeData(color: Colors.white),
      titleTextStyle: TextStyle(
        color: Colors.white,
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: primaryColor,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        textStyle: const TextStyle(fontSize: 16),
      ),
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: accentColor,
    ),
    inputDecorationTheme: InputDecorationTheme(
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(8),
        borderSide: const BorderSide(color: primaryColor, width: 2),
      ),
      prefixIconColor: primaryColor,
    ),
    cardTheme: CardTheme(
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
    ),
    textButtonTheme: TextButtonThemeData(
      style: TextButton.styleFrom(foregroundColor: primaryColor),
    ),
  );
}

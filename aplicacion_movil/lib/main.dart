import 'package:flutter/material.dart';
import 'screens/auth/logi_screen.dart';
import 'screens/student/dashboard_screen.dart';
import 'screens/student/materias_screen.dart';
import 'screens/student/asistencias_screen.dart';
import 'screens/student/materia/evaluaciones/evaluaciones_screen.dart';
import 'screens/student/rendimiento_screen.dart';
import 'screens/student/materia/asistencias/materia_detalle_screen.dart';
import 'screens/student/materia/evaluaciones/materia_evaluaciones_screen.dart';
import 'screens/student/materia/asistencias/materia_asistencias_screen.dart';
import 'screens/student/materia/evaluaciones/materia_tipo_evaluaciones_screen.dart';
import 'config/theme_config.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sistema Académico',
      theme: AppTheme.lightTheme,
      initialRoute: '/login',
      routes: {
        '/login': (context) => const LoginScreen(),
        '/student/dashboard': (context) => const StudentDashboardScreen(),
        '/student/materias': (context) => const MateriasScreen(),
        '/student/evaluaciones': (context) => const EvaluacionesScreen(),
        '/student/asistencias': (context) => const AsistenciasScreen(),
        '/student/rendimiento': (context) => const RendimientoScreen(),
        '/student/materia/detalle': (context) => const MateriaDetalleScreen(),
        '/student/materia/tipos-evaluacion':
            (context) => const MateriaTiposEvaluacionScreen(),
        '/student/materia/evaluaciones':
            (context) => const MateriaEvaluacionesScreen(),
        '/student/materia/asistencias':
            (context) => const MateriaAsistenciasScreen(),
        '/student/materia/tipo-evaluaciones':
            (context) => const MateriaTiposEvaluacionScreen(),
      },
    );
  }
}

import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';
import './firebase_options.dart'; // Añadir esta importación
import 'screens/auth/logi_screen.dart';
// Importaciones de Student
import 'screens/student/dashboard_screen.dart';
import 'screens/student/materias_screen.dart';
import 'screens/student/materia/asistencias/asistencias_screen.dart';
import 'screens/student/materia/evaluaciones/evaluaciones_screen.dart';
import 'screens/student/rendimiento_screen.dart';
import 'screens/student/materia/materia_detalle_screen.dart';
import 'screens/student/materia/evaluaciones/materia_evaluaciones_screen.dart';
import 'screens/student/materia/asistencias/materia_asistencias_screen.dart';
import 'screens/student/materia/evaluaciones/materia_tipo_evaluaciones_screen.dart';
import 'screens/student/materia/evaluaciones/detalles_tipo_evaluacion.dart';
import 'screens/student/materia/asistencias/registrar_asistencia_screen.dart';
import 'screens/student/calificaciones/anio_academico_screen.dart';
import 'screens/student/calificaciones/trimestre_screen.dart';
import 'screens/student/calificaciones/calificaciones_materia_screen.dart';
// Importaciones de Tutor
import 'screens/tutor/dashboard_tutor_screen.dart';
import 'screens/tutor/estudiantes/estudiantes_list_screen.dart';
import 'screens/tutor/estudiantes/estudiante_detalle_screen.dart'; // Añadida
import 'screens/tutor/calificaciones/anio_academico_screen.dart' as tutor;
import 'screens/tutor/calificaciones/estudiante_trimestre_screen.dart';
import 'screens/tutor/calificaciones/calificaciones_estudiante_screen.dart'; // Añadida
import 'config/theme_config.dart';
import 'services/notificaciones_service.dart';
import 'services/estudiante/monitor_automatico_service.dart';
import 'screens/student/alertas_rendimiento_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar Firebase antes de cualquier otra cosa
  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);

  runApp(MyApp());
}

// Modifica la clase MyApp para ser StatefulWidget en lugar de StatelessWidget
class MyApp extends StatefulWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  // ignore: library_private_types_in_public_api
  _MyAppState createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  @override
  void initState() {
    super.initState();
    // Inicializar servicio de notificaciones
    NotificacionesService.inicializar();

    // Iniciar monitoreo automático de rendimiento
    _iniciarMonitoreoAutomatico();
  }

  Future<void> _iniciarMonitoreoAutomatico() async {
    // Pequeña pausa para asegurar que Firebase esté inicializado
    await Future.delayed(Duration(seconds: 2));

    // Iniciar monitoreo una vez que la app esté cargada
    MonitorAutomaticoService.iniciar();
  }

  @override
  void dispose() {
    // Detener el monitoreo al cerrar la aplicación
    MonitorAutomaticoService.detener();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sistema Académico',
      theme: AppTheme.lightTheme,
      initialRoute: '/login',
      routes: {
        // Rutas de autenticación
        '/login': (context) => const LoginScreen(),

        // Rutas para estudiantes
        '/student/dashboard': (context) => const StudentDashboardScreen(),
        '/student/materias': (context) => const MateriasScreen(),
        '/student/evaluaciones': (context) => const EvaluacionesScreen(),
        '/student/asistencias': (context) => const AsistenciasScreen(),
        '/student/rendimiento': (context) {
          final args = ModalRoute.of(context)!.settings.arguments;
          if (args == null ||
              args is! Map<String, dynamic> ||
              !args.containsKey('estudianteId')) {
            // Puedes mostrar una pantalla de error o redirigir
            return Scaffold(
              appBar: AppBar(title: const Text('Error')),
              body: const Center(
                child: Text('Faltan argumentos para mostrar el rendimiento.'),
              ),
            );
          }
          return RendimientoScreen(
            estudianteId: args['estudianteId'],
            estudianteCodigo: args['estudianteCodigo'],
          );
        },
        '/student/materia/detalle': (context) => const MateriaDetalleScreen(),
        '/student/materia/tipos-evaluacion':
            (context) => const MateriaTiposEvaluacionScreen(),
        '/student/materia/evaluaciones':
            (context) => const MateriaEvaluacionesScreen(),
        '/student/materia/asistencias':
            (context) => const MateriaAsistenciasScreen(),
        '/student/materia/tipo-evaluaciones':
            (context) => const MateriaTiposEvaluacionScreen(),
        '/student/materia/detalles-tipo-evaluacion':
            (context) => const DetallesTipoEvaluacionScreen(),
        '/student/materia/registrar-asistencia':
            (context) => const RegistrarAsistenciaScreen(),
        '/student/calificaciones/':
            (context) => const AnioAcademicoScreen(
              titulo: 'Años Académicos',
              nextRoute: '/estudiante/trimestres',
            ),
        '/estudiante/trimestres': (context) => const TrimestresScreen(),
        '/estudiante/calificaciones/materia':
            (context) => const CalificacionesMateriaScreen(),

        // Rutas para tutores
        '/tutor/dashboard': (context) => const DashboardTutorScreen(),
        '/tutor/estudiantes': (context) => const EstudiantesListScreen(),
        '/tutor/anios-academicos':
            (context) => const tutor.AnioAcademicoScreen(),
        '/tutor/estudiantes-anio': (context) {
          final args =
              ModalRoute.of(context)!.settings.arguments
                  as Map<String, dynamic>;
          return EstudiantesAnioScreen(anioAcademico: args['anio']);
        },
        '/tutor/calificaciones-estudiante': (context) {
          final args =
              ModalRoute.of(context)!.settings.arguments
                  as Map<String, dynamic>;
          return CalificacionesEstudianteScreen(
            estudiante: args['estudiante'],
            anioAcademico: args['anio'],
          );
        },
        '/tutor/estudiante-detalle': (context) {
          final args =
              ModalRoute.of(context)!.settings.arguments
                  as Map<String, dynamic>;
          return EstudianteDetalleScreen(estudiante: args['estudiante']);
        },
        '/student/alertas': (context) => AlertasRendimientoScreen(),
      },
      // Manejar rutas desconocidas
      onUnknownRoute: (settings) {
        // Redirigir a login si la ruta no existe
        return MaterialPageRoute(builder: (context) => const LoginScreen());
      },
    );
  }
}

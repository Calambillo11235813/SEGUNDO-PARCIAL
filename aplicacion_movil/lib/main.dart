import 'package:flutter/material.dart';
import 'screens/auth/logi_screen.dart';
import 'screens/student/dashboard_screen.dart';
import 'screens/teacher/dashboard_screen.dart';
import 'services/auth_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Sistema Académico',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      initialRoute: '/',
      routes: {
        '/': (context) => const SplashScreen(),
        '/login': (context) => const LoginScreen(),
        '/student/dashboard': (context) => const StudentDashboardScreen(),
        '/teacher/dashboard': (context) => const TeacherDashboardScreen(),
        '/dashboard': (context) => const PlaceholderWidget('Dashboard'),
      },
    );
  }
}

class PlaceholderWidget extends StatelessWidget {
  final String text;
  const PlaceholderWidget(this.text, {super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(child: Text(text, style: const TextStyle(fontSize: 24))),
    );
  }
}

// SplashScreen para verificar la sesión
class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkSession();
  }

  Future<void> _checkSession() async {
    await Future.delayed(const Duration(seconds: 2)); // Simular carga

    final isLoggedIn = await AuthService.isLoggedIn();

    // Comprueba si el widget sigue montado después de la operación asíncrona
    if (!mounted) return;

    if (isLoggedIn) {
      // Verificar el rol del usuario
      final user = await AuthService.getCurrentUser();

      // Comprueba de nuevo si el widget sigue montado
      if (!mounted) return;

      if (user?.isEstudiante ?? false) {
        Navigator.pushReplacementNamed(context, '/student/dashboard');
      } else if (user?.isProfesor ?? false) {
        Navigator.pushReplacementNamed(context, '/teacher/dashboard');
      } else {
        Navigator.pushReplacementNamed(context, '/dashboard');
      }
    } else {
      // Comprueba de nuevo si el widget sigue montado
      if (!mounted) return;

      Navigator.pushReplacementNamed(context, '/login');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.school,
              size: 100,
              color: Theme.of(context).primaryColor,
            ),
            const SizedBox(height: 24),
            const Text(
              'Sistema Académico',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 24),
            const CircularProgressIndicator(),
          ],
        ),
      ),
    );
  }
}

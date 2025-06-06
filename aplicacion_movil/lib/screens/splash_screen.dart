import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../config/theme_config.dart'; // Añadir esta importación

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  Future<void> _checkLoginStatus() async {
    // Simular un pequeño retraso para mostrar la pantalla de splash
    await Future.delayed(const Duration(seconds: 2));

    try {
      final isLoggedIn = await AuthService.isLoggedIn();
      final user = isLoggedIn ? await AuthService.getCurrentUser() : null;

      if (mounted) {
        if (isLoggedIn && user != null) {
          if (user.rol?['nombre'] == 'Estudiante') {
            Navigator.pushReplacementNamed(context, '/student/dashboard');
          } else if (user.rol?['nombre'] == 'Profesor') {
            Navigator.pushReplacementNamed(context, '/teacher/dashboard');
          } else {
            Navigator.pushReplacementNamed(context, '/dashboard');
          }
        } else {
          Navigator.pushReplacementNamed(context, '/login');
        }
      }
    } catch (e) {
      if (mounted) {
        Navigator.pushReplacementNamed(context, '/login');
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo o nombre de la app con color MORADO
            Icon(
              Icons.school,
              size: 100,
              color: AppTheme.primaryColor, // Cambiado a morado
            ),
            const SizedBox(height: 24),
            Text(
              'Sistema Académico',
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryColor, // Cambiado a morado
              ),
            ),
            const SizedBox(height: 48),
            // Indicador de carga con color MORADO
            CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(
                AppTheme.primaryColor, // Asegurar que sea morado
              ),
            ),
            const SizedBox(height: 24),
            Text('Cargando...', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}

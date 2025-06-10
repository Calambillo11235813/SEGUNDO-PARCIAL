import 'package:flutter/material.dart';
import 'package:flutter/foundation.dart'; // Para usar kDebugMode
import '../../services/auth_service.dart';
import '../../config/theme_config.dart';
import '../../models/usuario.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _codigoController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();

  bool _isLoading = false;
  String _errorMessage = '';

  Future<void> _login() async {
    // Validación básica
    if (_codigoController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Por favor, ingresa tu código de usuario';
      });
      return;
    }

    if (_passwordController.text.isEmpty) {
      setState(() {
        _errorMessage = 'Por favor, ingresa tu contraseña';
      });
      return;
    }

    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final result = await AuthService.login(
        _codigoController.text.trim(),
        _passwordController.text,
      );

      // Verificar que el resultado contenga el usuario
      // CORRECCIÓN 1: Verificación más específica sin comparación innecesaria con null
      if (result.isEmpty || !result.containsKey('usuario')) {
        throw Exception('Error al obtener información del usuario');
      }

      // Crear el objeto Usuario desde el Map usando fromJson
      final usuarioData = result['usuario'] as Map<String, dynamic>;
      final usuario = Usuario.fromJson(usuarioData);

      if (!mounted) return;

      // Usar los getters del objeto Usuario
      if (usuario.isEstudiante) {
        Navigator.pushReplacementNamed(context, '/student/dashboard');
      } else if (usuario.isProfesor) {
        // Mostrar mensaje informativo
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text(
              'El módulo de profesor está en desarrollo. Serás redirigido a una página informativa.',
            ),
            duration: Duration(seconds: 3),
          ),
        );
        // Redirigir a la página placeholder
        Navigator.pushReplacementNamed(context, '/teacher/dashboard');
      } else if (usuario.rol != null && usuario.rol!['nombre'] == 'Tutor') {
        // Redirigir al dashboard de tutor
        Navigator.pushReplacementNamed(context, '/tutor/dashboard');
      } else {
        // Para casos donde el rol no está específicamente manejado
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(
              'Rol no reconocido: ${usuario.rol?['nombre'] ?? "desconocido"}',
            ),
            duration: const Duration(seconds: 3),
          ),
        );
        // Redirigir a una página por defecto o mantener en login
        setState(() {
          _errorMessage = 'Tu rol no tiene acceso a esta aplicación.';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });

      // CORRECCIÓN 2: Usar debugPrint solo en modo debug
      if (kDebugMode) {
        debugPrint('Error de login: $e');
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Center(
            child: SingleChildScrollView(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo o título
                  const Icon(
                    Icons.school,
                    size: 100,
                    color: AppTheme.primaryColor,
                  ),
                  const SizedBox(height: 24),

                  // Título
                  const Text(
                    'Sistema Académico',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Iniciar Sesión',
                    textAlign: TextAlign.center,
                    style: TextStyle(fontSize: 16, color: Colors.grey[700]),
                  ),
                  const SizedBox(height: 32),

                  // Campo de código
                  TextField(
                    controller: _codigoController,
                    decoration: const InputDecoration(
                      labelText: 'Código de Usuario',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.person),
                    ),
                    keyboardType: TextInputType.number,
                  ),
                  const SizedBox(height: 16),

                  // Campo de contraseña
                  TextField(
                    controller: _passwordController,
                    decoration: const InputDecoration(
                      labelText: 'Contraseña',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.lock),
                    ),
                    obscureText: true,
                  ),
                  const SizedBox(height: 8),

                  // Mensaje de error
                  if (_errorMessage.isNotEmpty)
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Text(
                        _errorMessage,
                        style: const TextStyle(color: Colors.red),
                        textAlign: TextAlign.center,
                      ),
                    ),

                  const SizedBox(height: 24),

                  // Botón de inicio de sesión
                  ElevatedButton(
                    onPressed: _isLoading ? null : _login,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryColor,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child:
                        _isLoading
                            ? const SizedBox(
                              height: 20,
                              width: 20,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                                valueColor: AlwaysStoppedAnimation<Color>(
                                  Colors.white,
                                ),
                              ),
                            )
                            : const Text('INICIAR SESIÓN'),
                  ),

                  const SizedBox(height: 16),

                  // Texto de ayuda
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Text('¿Olvidaste tu contraseña? '),
                      TextButton(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text(
                                'Contacta a tu administrador para restablecer tu contraseña',
                              ),
                              duration: Duration(seconds: 4),
                            ),
                          );
                        },
                        child: const Text('Contacta a tu administrador'),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

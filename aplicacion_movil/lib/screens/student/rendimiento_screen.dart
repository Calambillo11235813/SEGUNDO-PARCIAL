import 'package:flutter/material.dart';
import '../../models/usuario.dart';
import '../../services/auth_service.dart';
import '../../widgets/student_drawer.dart';

class RendimientoScreen extends StatefulWidget {
  const RendimientoScreen({super.key});

  @override
  State<RendimientoScreen> createState() => _RendimientoScreenState();
}

class _RendimientoScreenState extends State<RendimientoScreen> {
  bool isLoading = true;
  Usuario? currentUser;
  String? errorMessage;

  @override
  void initState() {
    super.initState();
    _loadUserData();
  }

  Future<void> _loadUserData() async {
    try {
      final user = await AuthService.getCurrentUser();
      setState(() {
        currentUser = user;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = 'Error al cargar datos del usuario: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mi Rendimiento')),
      drawer:
          currentUser != null
              ? StudentDrawer(
                currentUser: currentUser,
                currentRoute: '/student/rendimiento',
              )
              : null,
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : errorMessage != null
              ? Center(child: Text(errorMessage!))
              : Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.insights, size: 100, color: Colors.blue),
                    const SizedBox(height: 20),
                    const Text(
                      'Estadísticas de Rendimiento',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 10),
                    const Text(
                      'Próximamente',
                      style: TextStyle(fontSize: 16, color: Colors.grey),
                    ),
                    const SizedBox(height: 40),
                    ElevatedButton(
                      onPressed: () {},
                      child: const Text('Ver detalles'),
                    ),
                  ],
                ),
              ),
    );
  }
}

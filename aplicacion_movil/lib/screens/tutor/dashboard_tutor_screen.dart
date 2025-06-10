import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';
import 'package:aplicacion_movil/widgets/dashboard_appbar.dart'; // Corregida la importación
import 'package:aplicacion_movil/widgets/tutor_drawer.dart';
import 'package:aplicacion_movil/models/usuario.dart';

class DashboardTutorScreen extends StatefulWidget {
  const DashboardTutorScreen({super.key}); // Corregido para usar super.key

  @override
  State<DashboardTutorScreen> createState() => _DashboardTutorScreenState();
}

class _DashboardTutorScreenState extends State<DashboardTutorScreen> {
  bool _isLoading = true;
  Usuario? _usuario;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadUserInfo();
  }

  Future<void> _loadUserInfo() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final usuario = await AuthService.getCurrentUser();

      setState(() {
        _usuario = usuario;
        _isLoading = false;
      });
    } catch (e) {
      AppLogger.e("Error cargando información del usuario: $e");
      setState(() {
        _error = "No se pudo cargar la información del usuario";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: DashboardAppBar(
        title: 'Panel de Tutor',
        subtitle: _usuario?.nombreCompleto ?? 'Cargando...',
        onRefresh: _loadUserInfo,
      ),
      // Agregar el drawer
      drawer: TutorDrawer(
        currentUser: _usuario,
        currentRoute: '/tutor/dashboard',
      ),
      body:
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
              ? Center(
                child: Text(_error!, style: const TextStyle(color: Colors.red)),
              )
              : _buildDashboardContent(),
    );
  }

  Widget _buildDashboardContent() {
    return RefreshIndicator(
      onRefresh: _loadUserInfo,
      child: SingleChildScrollView(
        physics: const AlwaysScrollableScrollPhysics(),
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Mensaje de bienvenida
            Text(
              'Bienvenido, ${_usuario?.nombre}',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryColor,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Accede rápidamente a la información de tus estudiantes',
              style: TextStyle(fontSize: 16, color: Colors.grey[600]),
            ),
            const SizedBox(height: 24),

            // Tarjetas de acceso rápido
            _buildOptionsGrid(),

            const SizedBox(height: 24),

            // Sección de estudiantes recientes
            const Text(
              'Estudiantes Recientes',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            _buildRecentStudentsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildOptionsGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16.0,
      mainAxisSpacing: 16.0,
      children: [
        _buildOptionCard(
          'Mis Estudiantes',
          Icons.people,
          Colors.blue,
          () => Navigator.pushNamed(context, '/tutor/estudiantes'),
        ),
        _buildOptionCard(
          'Calificaciones',
          Icons.assessment,
          Colors.green,
          () => Navigator.pushNamed(context, '/tutor/anios-academicos'),
        ),
        _buildOptionCard(
          'Estadísticas',
          Icons.bar_chart,
          Colors.orange,
          () => Navigator.pushNamed(context, '/tutor/estadisticas'),
        ),
        _buildOptionCard(
          'Asistencias',
          Icons.calendar_today,
          Colors.purple,
          () => Navigator.pushNamed(context, '/tutor/asistencias'),
        ),
      ],
    );
  }

  Widget _buildOptionCard(
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 48, color: color),
              const SizedBox(height: 12),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildRecentStudentsSection() {
    // Normalmente aquí cargaríamos los estudiantes recientes
    // Por ahora mostraremos un mensaje de "Cargando..."
    return const Card(
      child: Padding(
        padding: EdgeInsets.all(16.0),
        child: Center(
          child: Text(
            "Cargando estudiantes recientes...",
            style: TextStyle(color: Colors.grey),
          ),
        ),
      ),
    );
  }
}

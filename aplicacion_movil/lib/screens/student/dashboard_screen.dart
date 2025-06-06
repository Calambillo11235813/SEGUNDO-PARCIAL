import 'package:flutter/material.dart';
import '../../services/auth_service.dart';
import '../../models/usuario.dart';
import '../../widgets/student_drawer.dart';
// Importar el tema
import '../../config/theme_config.dart';

class StudentDashboardScreen extends StatefulWidget {
  const StudentDashboardScreen({super.key});

  @override
  // ignore: library_private_types_in_public_api
  _StudentDashboardScreenState createState() => _StudentDashboardScreenState();
}

class _StudentDashboardScreenState extends State<StudentDashboardScreen> {
  Usuario? currentUser;
  bool isLoading = true;

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
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Panel de Estudiante')),
      drawer:
          currentUser != null
              ? StudentDrawer(
                currentUser: currentUser,
                currentRoute: '/student/dashboard',
              )
              : null,
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Tarjeta de información del usuario
                    Card(
                      elevation: 4,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              'Bienvenido, ${currentUser?.nombreCompleto ?? "Estudiante"}',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 8),
                            Text('Código: ${currentUser?.codigo ?? ""}'),
                            Text('Rol: ${currentUser?.rolNombre ?? ""}'),
                            const SizedBox(height: 16),
                            const Text(
                              'Resumen académico del semestre actual',
                              style: TextStyle(
                                color: Colors.grey,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Título de estadísticas
                    const Text(
                      'Estadísticas Generales',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 16),

                    // Grid de estadísticas
                    Expanded(
                      child: GridView.count(
                        crossAxisCount: 2,
                        mainAxisSpacing: 16,
                        crossAxisSpacing: 16,
                        childAspectRatio: 1.2,
                        children: [
                          _buildStatCard(
                            'Materias Inscritas',
                            '8',
                            Icons.book_outlined,
                            AppTheme.materiasColor,
                            'Total de materias este semestre',
                          ),
                          _buildStatCard(
                            'Promedio General',
                            '8.5',
                            Icons.grade_outlined,
                            AppTheme.calificacionesColor,
                            'Promedio acumulado actual',
                          ),
                          _buildStatCard(
                            'Asistencia',
                            '92%',
                            Icons.calendar_today_outlined,
                            AppTheme.asistenciaColor,
                            'Porcentaje de asistencia',
                          ),
                          _buildStatCard(
                            'Calificaciones',
                            '24',
                            Icons.assignment_turned_in_outlined,
                            AppTheme.rendimientoColor,
                            'Evaluaciones registradas',
                          ),
                          _buildStatCard(
                            'Créditos',
                            '18',
                            Icons.school_outlined,
                            AppTheme.primaryColor,
                            'Créditos inscritos',
                          ),
                          _buildStatCard(
                            'Actividades',
                            '12',
                            Icons.event_note_outlined,
                            AppTheme.accentColor,
                            'Tareas y proyectos pendientes',
                          ),
                        ],
                      ),
                    ),

                    // Sección de progreso académico
                    const SizedBox(height: 16),
                    Card(
                      elevation: 4,
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Progreso Académico',
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(height: 12),
                            _buildProgressItem(
                              'Créditos Completados',
                              85,
                              '153/180 créditos',
                              AppTheme.successColor,
                            ),
                            const SizedBox(height: 8),
                            _buildProgressItem(
                              'Semestre Actual',
                              60,
                              '60% completado',
                              AppTheme.primaryColor,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ),
    );
  }

  Widget _buildStatCard(
    String title,
    String value,
    IconData icon,
    Color color,
    String subtitle,
  ) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 32, color: color),
            const SizedBox(height: 8),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 4),
            Text(
              subtitle,
              style: TextStyle(fontSize: 10, color: Colors.grey[600]),
              textAlign: TextAlign.center,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProgressItem(
    String title,
    double progress,
    String subtitle,
    Color color,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
            Text(
              subtitle,
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: progress / 100,
          backgroundColor: Colors.grey[300],
          valueColor: AlwaysStoppedAnimation<Color>(color),
        ),
      ],
    );
  }
}

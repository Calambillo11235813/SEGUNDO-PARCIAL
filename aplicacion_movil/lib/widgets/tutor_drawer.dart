import 'package:flutter/material.dart';
import '../models/usuario.dart';
import '../services/auth_service.dart';
import '../config/theme_config.dart';

class TutorDrawer extends StatelessWidget {
  final Usuario? currentUser;
  final String currentRoute;

  const TutorDrawer({
    super.key,
    required this.currentUser,
    required this.currentRoute,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: Column(
        children: [
          // Encabezado del drawer con información del usuario
          UserAccountsDrawerHeader(
            accountName: Text(currentUser?.nombreCompleto ?? 'Tutor'),
            accountEmail: Text(currentUser?.codigo ?? ""),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                currentUser?.nombre[0].toUpperCase() ?? 'T',
                style: const TextStyle(
                  fontSize: 24.0,
                  color: AppTheme.primaryColor,
                ),
              ),
            ),
            decoration: const BoxDecoration(color: AppTheme.primaryColor),
          ),

          // Opciones del menú
          _buildMenuItem(
            context: context,
            title: 'Panel Principal',
            icon: Icons.dashboard,
            route: '/tutor/dashboard',
            isSelected: currentRoute == '/tutor/dashboard',
          ),

          _buildMenuItem(
            context: context,
            title: 'Estudiantes',
            icon: Icons.people,
            route: '/tutor/estudiantes',
            isSelected: currentRoute == '/tutor/estudiantes',
          ),

          _buildMenuItem(
            context: context,
            title: 'Calificaciones',
            icon: Icons.assessment,
            route: '/tutor/anios-academicos',
            isSelected: currentRoute == '/tutor/anios-academicos',
          ),

          _buildMenuItem(
            context: context,
            title: 'Estadísticas',
            icon: Icons.bar_chart,
            route: '/tutor/estadisticas',
            isSelected: currentRoute == '/tutor/estadisticas',
          ),

          _buildMenuItem(
            context: context,
            title: 'Asistencias',
            icon: Icons.calendar_today,
            route: '/tutor/asistencias',
            isSelected: currentRoute == '/tutor/asistencias',
          ),

          const Spacer(),
          const Divider(),

          // Opción para cerrar sesión
          ListTile(
            leading: const Icon(Icons.exit_to_app, color: Colors.red),
            title: const Text(
              'Cerrar Sesión',
              style: TextStyle(color: Colors.red),
            ),
            onTap: () async {
              await AuthService.logout();
              if (context.mounted) {
                Navigator.pushReplacementNamed(context, '/login');
              }
            },
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem({
    required BuildContext context,
    required String title,
    required IconData icon,
    required String route,
    required bool isSelected,
  }) {
    return ListTile(
      leading: Icon(
        icon,
        color: isSelected ? AppTheme.primaryColor : Colors.grey,
      ),
      title: Text(
        title,
        style: TextStyle(
          color: isSelected ? AppTheme.primaryColor : null,
          fontWeight: isSelected ? FontWeight.bold : null,
        ),
      ),
      selected: isSelected,
      selectedTileColor:
          isSelected ? AppTheme.primaryColor.withOpacity(0.1) : null,
      onTap: () {
        if (route != currentRoute) {
          Navigator.pop(context); // Cerrar el drawer

          // Si ya estamos en una ruta del tutor, usamos pushReplacementNamed
          // para evitar apilar pantallas innecesariamente
          if (currentRoute.startsWith('/tutor/')) {
            Navigator.pushReplacementNamed(context, route);
          } else {
            Navigator.pushNamed(context, route);
          }
        } else {
          Navigator.pop(context); // Solo cerramos el drawer
        }
      },
    );
  }
}

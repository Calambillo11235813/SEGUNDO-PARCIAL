import 'package:flutter/material.dart';
import '../models/usuario.dart';
import '../services/auth_service.dart';
import '../config/theme_config.dart'; // Importar el tema

class StudentDrawer extends StatelessWidget {
  final Usuario? currentUser;
  final String currentRoute;

  const StudentDrawer({
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
            accountName: Text(currentUser?.nombreCompleto ?? 'Estudiante'),
            accountEmail: Text('Código: ${currentUser?.codigo ?? ""}'),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              child: Text(
                currentUser?.nombre[0].toUpperCase() ?? 'E',
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
            title: 'Inicio',
            icon: Icons.home,
            route: '/student/dashboard',
            isSelected: currentRoute == '/student/dashboard',
          ),

          _buildMenuItem(
            context: context,
            title: 'Materias',
            icon: Icons.book,
            route: '/student/materias',
            isSelected: currentRoute == '/student/materias',
          ),

          ListTile(
            leading: const Icon(Icons.star),
            title: const Text('Calificaciones'),
            onTap: () {
              Navigator.pushNamed(context, '/student/calificaciones/');
              // O cierra el drawer primero si es necesario
              // Navigator.pop(context);
              // Navigator.pushNamed(context, '/student/calificaciones/');
            },
          ),

          _buildMenuItem(
            context: context,
            title: 'Asistencias',
            icon: Icons.calendar_today,
            route: '/student/asistencias',
            isSelected: currentRoute == '/student/asistencias',
          ),

          _buildMenuItem(
            context: context,
            title: 'Rendimiento',
            icon: Icons.insights,
            route: '/student/rendimiento',
            isSelected: currentRoute == '/student/rendimiento',
            onTap: () {
              Navigator.pop(context);
              Navigator.pushNamed(
                context,
                '/student/rendimiento',
                arguments: {
                  'estudianteId': currentUser?.id,
                  'estudianteCodigo': currentUser?.codigo,
                },
              );
            },
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
    VoidCallback? onTap, // <-- Agrega esto
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
          isSelected
              ? AppTheme.primaryColor.withAlpha((0.1 * 255).toInt())
              : null,
      onTap:
          onTap ??
          () {
            if (route != currentRoute) {
              Navigator.pop(context); // Cerrar el drawer
              if (currentRoute.startsWith('/student/')) {
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

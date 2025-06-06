import 'package:flutter/material.dart';
import '../../../config/theme_config.dart';

class MateriaDetalleScreen extends StatefulWidget {
  const MateriaDetalleScreen({super.key});

  @override
  State<MateriaDetalleScreen> createState() => _MateriaDetalleScreenState();
}

class _MateriaDetalleScreenState extends State<MateriaDetalleScreen> {
  Map<String, dynamic>? arguments;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    arguments ??=
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
  }

  @override
  Widget build(BuildContext context) {
    if (arguments == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: const Center(
          child: Text('Error: No se encontraron datos de la materia'),
        ),
      );
    }

    final materia = arguments!['materia'] as Map<String, dynamic>;
    final curso = arguments!['curso'] as Map<String, dynamic>;

    return Scaffold(
      appBar: AppBar(title: Text(materia['nombre'])),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Información de la materia
            _buildMateriaInfo(materia, curso),

            const SizedBox(height: 24),

            // Solo mostrar acciones principales
            _buildAccionesPrincipales(materia, curso),

            const SizedBox(height: 24),

            // Información del profesor (si existe)
            if (materia['profesor'] != null) _buildProfesorInfo(materia),
          ],
        ),
      ),
    );
  }

  Widget _buildMateriaInfo(
    Map<String, dynamic> materia,
    Map<String, dynamic> curso,
  ) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              materia['nombre'],
              style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Curso: ${curso['nombre']}',
              style: const TextStyle(fontSize: 16, color: Colors.grey),
            ),
            if (curso['nivel'] != null) ...[
              const SizedBox(height: 4),
              Text(
                'Nivel: ${curso['nivel']['nombre']}',
                style: const TextStyle(fontSize: 16, color: Colors.grey),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildAccionesPrincipales(
    Map<String, dynamic> materia,
    Map<String, dynamic> curso,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Acciones',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),

        Row(
          children: [
            Expanded(
              child: _buildActionCard(
                context,
                'Evaluaciones',
                Icons.assignment,
                AppTheme.calificacionesColor,
                () {
                  // CAMBIO: Navegar a tipos de evaluación en lugar de todas las evaluaciones
                  Navigator.pushNamed(
                    context,
                    '/student/materia/tipos-evaluacion',
                    arguments: {'materia': materia, 'curso': curso},
                  );
                },
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildActionCard(
                context,
                'Asistencias',
                Icons.calendar_today,
                AppTheme.asistenciaColor,
                () {
                  Navigator.pushNamed(
                    context,
                    '/student/materia/asistencias',
                    arguments: {'materia': materia, 'curso': curso},
                  );
                },
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildProfesorInfo(Map<String, dynamic> materia) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Profesor',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ListTile(
              leading: CircleAvatar(
                backgroundColor: AppTheme.primaryColor,
                child: Text(
                  materia['profesor']['nombre'][0].toUpperCase(),
                  style: const TextStyle(color: Colors.white),
                ),
              ),
              title: Text(
                '${materia['profesor']['nombre']} ${materia['profesor']['apellido']}',
              ),
              subtitle: const Text('Profesor asignado'),
              trailing: IconButton(
                icon: const Icon(Icons.message),
                onPressed: () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(
                      content: Text('Función de mensaje no implementada'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildActionCard(
    BuildContext context,
    String title,
    IconData icon,
    Color color,
    VoidCallback onTap,
  ) {
    return Card(
      elevation: 4,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 32, color: color),
              const SizedBox(height: 8),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

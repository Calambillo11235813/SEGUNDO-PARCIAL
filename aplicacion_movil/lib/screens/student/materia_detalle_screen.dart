import 'package:flutter/material.dart';

class MateriaDetalleScreen extends StatefulWidget {
  final Map<String, dynamic> materia;
  final Map<String, dynamic> curso;

  const MateriaDetalleScreen({
    super.key,
    required this.materia,
    required this.curso,
  });

  @override
  State<MateriaDetalleScreen> createState() => _MateriaDetalleScreenState();
}

class _MateriaDetalleScreenState extends State<MateriaDetalleScreen> {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.materia['nombre']),
        actions: [
          if (widget.materia['profesor'] != null)
            IconButton(
              icon: const Icon(Icons.message),
              onPressed: () {
                // Implementar función para contactar al profesor
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Función de mensaje no implementada'),
                  ),
                );
              },
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Información del curso
            Card(
              margin: const EdgeInsets.only(bottom: 16),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Curso: ${widget.curso['nombre']}',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    if (widget.curso['nivel'] != null)
                      Text('Nivel: ${widget.curso['nivel']['nombre']}'),
                  ],
                ),
              ),
            ),

            // Información del profesor
            if (widget.materia['profesor'] != null) ...[
              const Text(
                'Profesor',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              Card(
                margin: const EdgeInsets.only(bottom: 16),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.blue,
                    child: Text(
                      widget.materia['profesor']['nombre'][0].toUpperCase(),
                      style: const TextStyle(color: Colors.white),
                    ),
                  ),
                  title: Text(
                    '${widget.materia['profesor']['nombre']} ${widget.materia['profesor']['apellido']}',
                  ),
                  subtitle: const Text('Profesor asignado'),
                ),
              ),
            ],

            // Acciones rápidas
            const Text(
              'Acciones rápidas',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildActionCard(
                    context,
                    'Ver evaluaciones',
                    Icons.assignment,
                    () {
                      // Navegar a evaluaciones filtradas por esta materia
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            'Navegación a evaluaciones no implementada',
                          ),
                        ),
                      );
                    },
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildActionCard(
                    context,
                    'Ver asistencia',
                    Icons.calendar_today,
                    () {
                      // Navegar a asistencia filtrada por esta materia
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(
                          content: Text(
                            'Navegación a asistencia no implementada',
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
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
    VoidCallback onTap,
  ) {
    return Card(
      child: InkWell(
        onTap: onTap,
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(icon, size: 32, color: Colors.blue),
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

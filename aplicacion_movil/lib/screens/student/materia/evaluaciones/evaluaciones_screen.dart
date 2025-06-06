import 'package:flutter/material.dart';
import '../../../../config/theme_config.dart';

class EvaluacionesScreen extends StatelessWidget {
  final String? filtroMateriaId;
  final String? nombreMateria;

  const EvaluacionesScreen({
    super.key,
    this.filtroMateriaId,
    this.nombreMateria,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(nombreMateria ?? 'Evaluaciones')),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Aquí puedes mostrar una lista de evaluaciones filtradas por materiaId
          Card(
            child: ListTile(
              leading: Icon(Icons.assignment, color: AppTheme.primaryColor),
              title: const Text('Examen Parcial 1'),
              subtitle: const Text('Fecha: 20/06/2025 • Peso: 30%'),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.green.withAlpha(26), // 0.1 * 255 ≈ 26
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'Publicado',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.green,
                  ),
                ),
              ),
              onTap: () {
                // Navegar al detalle de la evaluación
              },
            ),
          ),
          const SizedBox(height: 8),
          Card(
            child: ListTile(
              leading: Icon(Icons.assignment, color: AppTheme.primaryColor),
              title: const Text('Examen Parcial 2'),
              subtitle: const Text('Fecha: 20/07/2025 • Peso: 30%'),
              trailing: Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: Colors.orange.withAlpha(26), // 0.1 * 255 ≈ 26
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Text(
                  'Pendiente',
                  style: TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.orange,
                  ),
                ),
              ),
              onTap: () {
                // Navegar al detalle de la evaluación
              },
            ),
          ),
        ],
      ),
    );
  }
}

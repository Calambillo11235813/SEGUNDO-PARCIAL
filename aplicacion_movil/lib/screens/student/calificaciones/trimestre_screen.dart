import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:aplicacion_movil/services/auth_service.dart';

class TrimestresScreen extends StatelessWidget {
  const TrimestresScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Obtener los argumentos
    final arguments =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>;
    final int anio = arguments['anio'];
    final List<dynamic> trimestres = arguments['trimestres'];

    return Scaffold(
      appBar: AppBar(title: Text('Trimestres $anio')),
      body: ListView.builder(
        padding: const EdgeInsets.all(16),
        itemCount: trimestres.length,
        itemBuilder: (context, index) {
          final trimestre = trimestres[index];
          final bool estaActivo = trimestre['estado'] == 'ACTIVO';

          return Card(
            elevation: 2,
            margin: const EdgeInsets.only(bottom: 16),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
              side: BorderSide(
                color: estaActivo ? Colors.green : Colors.grey.shade300,
                width: estaActivo ? 2 : 1,
              ),
            ),
            child: InkWell(
              onTap: () async {
                try {
                  // Obtener el ID del estudiante actual
                  final estudianteId = await AuthService.getCurrentUserId();

                  if (estudianteId != null) {
                    // Navegar a pantalla de calificaciones con IDs necesarios
                    Navigator.pushNamed(
                      context,
                      '/estudiante/calificaciones/materia',
                      arguments: {
                        'estudianteId': estudianteId,
                        'trimestreId': trimestre['id'],
                        'nombreTrimestre': trimestre['nombre'],
                      },
                    );
                  } else {
                    // Mostrar error si no se pudo obtener el ID
                    ScaffoldMessenger.of(context).showSnackBar(
                      const SnackBar(
                        content: Text(
                          'No se pudo obtener el ID del estudiante',
                        ),
                      ),
                    );
                  }
                } catch (e) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Error: ${e.toString()}')),
                  );
                }
              },
              borderRadius: BorderRadius.circular(12),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            trimestre['nombre'],
                            style: const TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        if (estaActivo)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.green,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text(
                              'ACTIVO',
                              style: TextStyle(
                                color: Colors.white,
                                fontWeight: FontWeight.bold,
                                fontSize: 12,
                              ),
                            ),
                          ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _buildDateRow(
                      'Inicio:',
                      trimestre['fecha_inicio'],
                      Icons.calendar_today,
                    ),
                    const SizedBox(height: 8),
                    _buildDateRow(
                      'Fin:',
                      trimestre['fecha_fin'],
                      Icons.event_available,
                    ),
                    const SizedBox(height: 12),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Nota mínima: ${trimestre['nota_minima_aprobacion']}',
                          style: const TextStyle(color: Colors.grey),
                        ),
                        Text(
                          'Asist. mínima: ${trimestre['porcentaje_asistencia_minima']}%',
                          style: const TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildDateRow(String label, String dateStr, IconData icon) {
    // Formatear la fecha
    final date = DateTime.parse(dateStr);
    final formattedDate = DateFormat('dd/MM/yyyy').format(date);

    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.grey[600]),
        const SizedBox(width: 8),
        Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
        const SizedBox(width: 4),
        Text(formattedDate, style: TextStyle(color: Colors.grey[700])),
      ],
    );
  }
}

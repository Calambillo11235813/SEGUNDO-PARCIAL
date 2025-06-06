// lib/screens/student/materia/materia_asistencias_screen.dart
import 'package:flutter/material.dart';
import 'asistencias_screen.dart';

class MateriaAsistenciasScreen extends StatelessWidget {
  const MateriaAsistenciasScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final arguments =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;

    if (arguments == null) {
      return const Scaffold(
        body: Center(
          child: Text('Error: No se encontraron datos de la materia'),
        ),
      );
    }

    final materia = arguments['materia'] as Map<String, dynamic>;

    return AsistenciasScreen(
      filtroMateriaId: materia['id'].toString(),
      nombreMateria: materia['nombre'],
    );
  }
}

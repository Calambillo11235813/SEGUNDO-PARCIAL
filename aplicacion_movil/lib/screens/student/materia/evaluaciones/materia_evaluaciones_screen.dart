// lib/screens/student/materia/materia_evaluaciones_screen.dart
import 'package:flutter/material.dart';
import 'evaluaciones_screen.dart'; // CORRECCIÓN: Importar del directorio actual

class MateriaEvaluacionesScreen extends StatelessWidget {
  const MateriaEvaluacionesScreen({super.key});

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

    return EvaluacionesScreen(
      filtroMateriaId: materia['id'].toString(),
      nombreMateria: materia['nombre'],
    );
  }
}

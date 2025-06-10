import 'package:flutter/material.dart';
import '../../../../services/auth_service.dart';
import '../../../../services/estudiante/evaluaciones_service.dart';
import '../../../../widgets/student_drawer.dart';
import '../../../../config/theme_config.dart';
import '../../../../models/usuario.dart';

class EvaluacionesScreen extends StatefulWidget {
  // Añadir parámetros para filtrar por materia
  final String? filtroMateriaId;
  final String? nombreMateria;

  const EvaluacionesScreen({
    super.key,
    this.filtroMateriaId,
    this.nombreMateria,
  });

  @override
  State<EvaluacionesScreen> createState() => _EvaluacionesScreenState();
}

class _EvaluacionesScreenState extends State<EvaluacionesScreen> {
  bool isLoading = true;
  String? error;
  List<dynamic> evaluaciones = [];
  // Año fijo 2025 - No se mostrará el selector
  final int anioFijo = 2025;
  Usuario? usuario;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _cargarEvaluaciones();
    });
  }

  Future<void> _cargarEvaluaciones() async {
    try {
      final arguments = ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
      
      if (arguments == null) {
        setState(() {
          error = 'No se recibieron parámetros';
          isLoading = false;
        });
        return;
      }

      final materiaInfo = arguments['materia'] as Map<String, dynamic>?;
      final anio = arguments['anio'] as int? ?? 2025;
      
      if (materiaInfo == null) {
        setState(() {
          error = 'No se recibió información de la materia';
          isLoading = false;
        });
        return;
      }

      final usuarioActual = await AuthService.getCurrentUser();
      
      if (usuarioActual == null) {
        setState(() {
          error = 'No hay sesión activa';
          isLoading = false;
        });
        return;
      }

      final estudianteId = usuarioActual.id.toString();
      final materiaId = materiaInfo['id'].toString();

      // Cargar evaluaciones con el filtro de materia y año
      final listaEvaluaciones = await EvaluacionesService.obtenerEvaluacionesPorEstudiante(
        estudianteId,
        materiaId: materiaId,
        anio: anio,
      );

      setState(() {
        evaluaciones = listaEvaluaciones;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        error = 'Error al cargar evaluaciones: $e';
        isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Título personalizado basado en la presencia de nombreMateria
    final String titulo =
        widget.nombreMateria != null
            ? 'Evaluaciones: ${widget.nombreMateria}'
            : 'Mis Evaluaciones 2025'; // Indicar el año en el título

    return Scaffold(
      appBar: AppBar(title: Text(titulo)),
      // Solo mostrar drawer cuando no estamos filtrando por materia
      drawer:
          widget.filtroMateriaId == null && usuario != null
              ? StudentDrawer(
                currentUser: usuario!,
                currentRoute: '/student/evaluaciones',
              )
              : null,
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : error != null
              ? Center(
                child: Text(error!, style: const TextStyle(color: Colors.red)),
              )
              : evaluaciones.isEmpty
              ? Center(
                child: Text(
                  widget.filtroMateriaId != null
                      ? 'No hay evaluaciones para ${widget.nombreMateria ?? "esta materia"} en 2025'
                      : 'No hay evaluaciones para el año 2025',
                ),
              )
              : ListView.builder(
                itemCount: evaluaciones.length,
                itemBuilder: (context, index) {
                  final evaluacion = evaluaciones[index];
                  return _buildEvaluacionCard(evaluacion);
                },
              ),
    );
  }

  // Widget para mostrar cada evaluación
  Widget _buildEvaluacionCard(dynamic evaluacion) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: ListTile(
        leading: Icon(Icons.assignment, color: AppTheme.primaryColor),
        title: Text(
          evaluacion['nombre'] ??
              evaluacion['titulo'] ??
              'Evaluación sin nombre',
        ),
        subtitle: Text(_buildSubtitleText(evaluacion)),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: _getStatusColor(evaluacion).withAlpha(26),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Text(
            evaluacion['estado'] ??
                (evaluacion['publicado'] ? 'Publicado' : 'No publicado'),
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
              color: _getStatusColor(evaluacion),
            ),
          ),
        ),
      ),
    );
  }

  String _buildSubtitleText(dynamic evaluacion) {
    // Determinar qué campo de fecha usar según el tipo de evaluación
    String fecha = '';
    if (evaluacion['tipo_objeto'] == 'participacion') {
      fecha = evaluacion['fecha_registro'] ?? 'Sin fecha';
    } else {
      fecha =
          evaluacion['fecha_entrega'] ??
          evaluacion['fecha_asignacion'] ??
          'Sin fecha';
    }

    // Obtener el porcentaje (puede estar en diferentes campos según la API)
    String porcentaje =
        evaluacion['peso']?.toString() ??
        evaluacion['porcentaje_nota_final']?.toString() ??
        '0';

    return 'Fecha: $fecha • Peso: $porcentaje%';
  }

  Color _getStatusColor(dynamic evaluacion) {
    // Determinar el color según el estado de la evaluación
    final estado = evaluacion['estado'] ?? '';
    final publicado = evaluacion['publicado'] ?? false;

    if (estado == 'Publicado' || publicado == true) {
      return Colors.green;
    } else if (estado == 'En progreso') {
      return Colors.orange;
    } else {
      return Colors.grey;
    }
  }
}

import 'package:flutter/material.dart';
import '../../../../config/theme_config.dart';
import '../../../../services/estudiante/materias_service.dart';

class MateriaTiposEvaluacionScreen extends StatefulWidget {
  const MateriaTiposEvaluacionScreen({super.key});

  @override
  State<MateriaTiposEvaluacionScreen> createState() =>
      _MateriaTiposEvaluacionScreenState();
}

class _MateriaTiposEvaluacionScreenState
    extends State<MateriaTiposEvaluacionScreen> {
  Map<String, dynamic>? tiposEvaluacionData;
  bool isLoading = true;
  String? error;
  Map<String, dynamic>? arguments;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    if (arguments == null) {
      arguments =
          ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;
      _cargarTiposEvaluacion();
    }
  }

  Future<void> _cargarTiposEvaluacion() async {
    if (arguments == null) {
      setState(() {
        error = 'No se encontraron datos de la materia';
        isLoading = false;
      });
      return;
    }

    try {
      final materia = arguments!['materia'] as Map<String, dynamic>;
      final materiaId = materia['id'];

      final data = await MateriasService.obtenerTiposEvaluacionPorMateria(
        materiaId,
      );

      if (mounted) {
        setState(() {
          tiposEvaluacionData = data;
          isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          error = e.toString();
          isLoading = false;
        });
      }
    }
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

    return Scaffold(
      appBar: AppBar(
        title: Text('Evaluaciones - ${materia['nombre']}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                isLoading = true;
                error = null;
              });
              _cargarTiposEvaluacion();
            },
          ),
          // Botón para ver todas las evaluaciones sin filtro
          IconButton(
            icon: const Icon(Icons.list),
            tooltip: 'Ver todas las evaluaciones',
            onPressed: () {
              Navigator.pushNamed(
                context,
                '/student/materia/evaluaciones',
                arguments: arguments,
              );
            },
          ),
        ],
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : error != null
              ? _buildErrorState()
              : _buildTiposEvaluacionContent(),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.error_outline, size: 64, color: Colors.red[300]),
          const SizedBox(height: 16),
          Text(
            'Error al cargar datos',
            style: Theme.of(context).textTheme.titleLarge,
          ),
          const SizedBox(height: 8),
          Text(
            error!,
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[600]),
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              setState(() {
                isLoading = true;
                error = null;
              });
              _cargarTiposEvaluacion();
            },
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildTiposEvaluacionContent() {
    if (tiposEvaluacionData == null) return const SizedBox.shrink();

    final tiposEvaluacion =
        tiposEvaluacionData!['tipos_evaluacion'] as List<dynamic>;

    if (tiposEvaluacion.isEmpty) {
      return _buildEmptyState();
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tipos de evaluación (ahora directamente sin espaciado adicional)
          _buildTiposEvaluacionGrid(tiposEvaluacion),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.assignment_outlined, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No hay evaluaciones registradas',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            'Las evaluaciones aparecerán aquí cuando el profesor las publique',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildTiposEvaluacionGrid(List<dynamic> tiposEvaluacion) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Tipos de Evaluación',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),

        GridView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            mainAxisSpacing: 12,
            crossAxisSpacing: 12,
            childAspectRatio: 1.2,
          ),
          itemCount: tiposEvaluacion.length,
          itemBuilder: (context, index) {
            final tipo = tiposEvaluacion[index];
            return _buildTipoEvaluacionCard(tipo);
          },
        ),
      ],
    );
  }

  Widget _buildTipoEvaluacionCard(Map<String, dynamic> tipo) {
    final colors = [
      AppTheme.calificacionesColor,
      AppTheme.asistenciaColor,
      AppTheme.rendimientoColor,
      AppTheme.materiasColor,
      AppTheme.accentColor,
    ];

    final colorIndex = tipo['id'] % colors.length;
    final color = colors[colorIndex];

    // Nueva función para obtener el texto apropiado
    final cantidadTexto = _getCantidadTexto(
      tipo['nombre'],
      tipo['cantidad_evaluaciones'],
    );

    return Card(
      elevation: 4,
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/student/materia/evaliones_screen',
            arguments: {
              'tipo_evaluacion': tipo,
              'materia': tiposEvaluacionData!['materia'],
            },
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: color.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(
                  _getIconForTipo(tipo['nombre']),
                  size: 24,
                  color: color,
                ),
              ),
              const SizedBox(height: 8),
              Text(
                tipo['nombre'],
                style: const TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                cantidadTexto, // CAMBIO: usar el texto personalizado
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  IconData _getIconForTipo(String tipoNombre) {
    switch (tipoNombre.toUpperCase()) {
      case 'EXAMEN':
        return Icons.quiz;
      case 'TAREA':
        return Icons.assignment;
      case 'PROYECTO':
        return Icons.work;
      case 'PARTICIPACION':
        return Icons.record_voice_over;
      case 'LABORATORIO':
        return Icons.science;
      case 'PRACTICOS':
        return Icons.science_outlined;
      default:
        return Icons.assignment_outlined;
    }
  }

  // NUEVO MÉTODO: Obtener el texto apropiado según el tipo
  String _getCantidadTexto(String tipoNombre, int cantidad) {
    switch (tipoNombre.toUpperCase()) {
      case 'EXAMEN':
        return cantidad == 1 ? '1 examen' : '$cantidad exámenes';
      case 'TAREA':
        return cantidad == 1 ? '1 tarea' : '$cantidad tareas';
      case 'PROYECTO':
        return cantidad == 1 ? '1 proyecto' : '$cantidad proyectos';
      case 'PARTICIPACION':
        return cantidad == 1 ? '1 participación' : '$cantidad participaciones';
      case 'LABORATORIO':
        return cantidad == 1 ? '1 laboratorio' : '$cantidad laboratorios';
      case 'PRACTICOS':
        return cantidad == 1 ? '1 práctico' : '$cantidad prácticos';
      case 'QUIZ':
        return cantidad == 1 ? '1 quiz' : '$cantidad quizzes';
      case 'ENSAYO':
        return cantidad == 1 ? '1 ensayo' : '$cantidad ensayos';
      case 'PRESENTACION':
        return cantidad == 1 ? '1 presentación' : '$cantidad presentaciones';
      default:
        return cantidad == 1 ? '1 evaluación' : '$cantidad evaluaciones';
    }
  }
}

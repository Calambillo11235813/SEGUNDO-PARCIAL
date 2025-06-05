import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../models/usuario.dart';
import '../../services/auth_service.dart';
import '../../services/estudiante/evaluaciones_service.dart';

class EvaluacionesScreen extends StatefulWidget {
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
  List<dynamic> evaluaciones = [];
  String? errorMessage;
  Usuario? currentUser;
  String? selectedMateriaId;

  // Para filtros
  List<Map<String, dynamic>> materias = []; // Ya no es final

  @override
  void initState() {
    super.initState();
    // Si viene con filtro de materia preestablecido
    if (widget.filtroMateriaId != null) {
      selectedMateriaId = widget.filtroMateriaId;
    }
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Obtener usuario actual
      final user = await AuthService.getCurrentUser();

      if (user == null) {
        setState(() {
          isLoading = false;
          errorMessage = 'No se pudo obtener la información del usuario';
        });
        return;
      }

      setState(() {
        currentUser = user;
      });

      // Cargar evaluaciones
      final data = await EvaluacionesService.obtenerEvaluacionesPorEstudiante(
        user.id.toString(),
        materiaId: selectedMateriaId,
      );

      // Extraer lista única de materias para el filtro
      final materiasSet = <String>{};
      final materiasLista = <Map<String, dynamic>>[];

      for (var evaluacion in data) {
        final materiaId = evaluacion['materia']['id'].toString();
        final materiaNombre = evaluacion['materia']['nombre'];

        if (!materiasSet.contains(materiaId)) {
          materiasSet.add(materiaId);
          materiasLista.add({'id': materiaId, 'nombre': materiaNombre});
        }
      }

      setState(() {
        evaluaciones = data;
        materias = materiasLista;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = 'Error al cargar las evaluaciones: $e';
      });
    }
  }

  Future<void> _filtrarPorMateria(String? materiaId) async {
    setState(() {
      isLoading = true;
      selectedMateriaId = materiaId;
    });

    await _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.nombreMateria != null
              ? 'Evaluaciones: ${widget.nombreMateria}'
              : 'Mis Evaluaciones',
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              _showFilterDialog(context);
            },
          ),
        ],
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : errorMessage != null
              ? Center(child: Text(errorMessage!))
              : _buildEvaluacionesList(),
    );
  }

  void _showFilterDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Filtrar por materia'),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView(
              shrinkWrap: true,
              children: [
                ListTile(
                  title: const Text('Todas las materias'),
                  selected: selectedMateriaId == null,
                  onTap: () {
                    Navigator.pop(context);
                    _filtrarPorMateria(null);
                  },
                ),
                ...materias.map(
                  (materia) => ListTile(
                    title: Text(materia['nombre']),
                    selected: selectedMateriaId == materia['id'],
                    onTap: () {
                      Navigator.pop(context);
                      _filtrarPorMateria(materia['id']);
                    },
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildEvaluacionesList() {
    if (evaluaciones.isEmpty) {
      return const Center(child: Text('No hay evaluaciones disponibles'));
    }

    return ListView.builder(
      itemCount: evaluaciones.length,
      itemBuilder: (context, index) {
        final evaluacion = evaluaciones[index];
        final calificacion = evaluacion['calificacion'];

        // Formatear fechas
        final fechaAsignacion = DateFormat(
          'dd/MM/yyyy',
        ).format(DateTime.parse(evaluacion['fecha_asignacion']));
        final fechaEntrega = DateFormat(
          'dd/MM/yyyy',
        ).format(DateTime.parse(evaluacion['fecha_entrega']));

        // Determinar color según estado
        Color statusColor = Colors.grey;
        IconData statusIcon = Icons.access_time;
        String statusText = 'Pendiente';

        final DateTime fechaActual = DateTime.now();
        final DateTime fechaLimite = DateTime.parse(
          evaluacion['fecha_entrega'],
        );

        if (calificacion != null) {
          statusColor =
              calificacion['nota_final'] >= evaluacion['nota_minima_aprobacion']
                  ? Colors.green
                  : Colors.red;
          statusIcon =
              calificacion['nota_final'] >= evaluacion['nota_minima_aprobacion']
                  ? Icons.check_circle
                  : Icons.cancel;
          statusText =
              calificacion['nota_final'] >= evaluacion['nota_minima_aprobacion']
                  ? 'Aprobado'
                  : 'Reprobado';
        } else if (fechaActual.isAfter(fechaLimite)) {
          statusColor = Colors.red;
          statusIcon = Icons.warning;
          statusText = 'Vencido';
        }

        return Card(
          margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: ExpansionTile(
            leading: CircleAvatar(
              backgroundColor: statusColor.withAlpha((255 * 0.2).round()),
              child: Icon(statusIcon, color: statusColor),
            ),
            title: Text(
              evaluacion['titulo'],
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${evaluacion['materia']['nombre']} • ${evaluacion['tipo_evaluacion']['nombre']}',
                ),
                Text(
                  'Entrega: $fechaEntrega • ${evaluacion['porcentaje_nota_final']}%',
                ),
              ],
            ),
            trailing:
                calificacion != null
                    ? Text(
                      '${calificacion['nota_final']}/${evaluacion['nota_maxima']}',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: statusColor,
                        fontSize: 16,
                      ),
                    )
                    : const Icon(Icons.keyboard_arrow_down),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    if (evaluacion['descripcion'] != null &&
                        evaluacion['descripcion'].isNotEmpty) ...[
                      const Text(
                        'Descripción:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      Text(evaluacion['descripcion']),
                      const SizedBox(height: 8),
                    ],

                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Fecha asignación: $fechaAsignacion'),
                        Text('Fecha entrega: $fechaEntrega'),
                      ],
                    ),

                    const SizedBox(height: 8),

                    calificacion != null
                        ? _buildCalificacionDetails(calificacion, evaluacion)
                        : _buildNoCalificacion(statusText),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildCalificacionDetails(
    Map<String, dynamic> calificacion,
    Map<String, dynamic> evaluacion,
  ) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Divider(),
        const Text(
          'Calificación:',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),

        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text('Nota: ${calificacion['nota']}/${evaluacion['nota_maxima']}'),
            Text(
              'Nota final: ${calificacion['nota_final']}/${evaluacion['nota_maxima']}',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color:
                    calificacion['nota_final'] >=
                            evaluacion['nota_minima_aprobacion']
                        ? Colors.green
                        : Colors.red,
              ),
            ),
          ],
        ),

        if (calificacion['entrega_tardia']) ...[
          const SizedBox(height: 4),
          Text(
            'Entrega tardía: Penalización del ${evaluacion['penalizacion_tardio']}%',
            style: const TextStyle(color: Colors.orange),
          ),
        ],

        if (calificacion['observaciones'] != null &&
            calificacion['observaciones'].isNotEmpty) ...[
          const SizedBox(height: 8),
          const Text(
            'Observaciones:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(calificacion['observaciones']),
        ],

        if (calificacion['retroalimentacion'] != null &&
            calificacion['retroalimentacion'].isNotEmpty) ...[
          const SizedBox(height: 8),
          const Text(
            'Retroalimentación:',
            style: TextStyle(fontWeight: FontWeight.bold),
          ),
          Text(calificacion['retroalimentacion']),
        ],
      ],
    );
  }

  Widget _buildNoCalificacion(String statusText) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.center,
      children: [
        const Divider(),
        Text(
          'Estado: $statusText',
          style: TextStyle(
            fontWeight: FontWeight.bold,
            color: statusText == 'Vencido' ? Colors.red : Colors.grey,
          ),
        ),
        const SizedBox(height: 8),
        const Text('Esta evaluación aún no ha sido calificada.'),
      ],
    );
  }
}

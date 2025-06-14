import 'package:flutter/material.dart';
import 'dart:convert'; // Importar para JsonEncoder
import '../../../../services/estudiante/evaluaciones_service.dart';
import '../../../../services/auth_service.dart';
import '../../../../utils/logger.dart'; // Asegúrate de importar el logger

class DetallesTipoEvaluacionScreen extends StatefulWidget {
  const DetallesTipoEvaluacionScreen({super.key});

  @override
  State<DetallesTipoEvaluacionScreen> createState() =>
      _DetallesTipoEvaluacionScreenState();
}

class _DetallesTipoEvaluacionScreenState
    extends State<DetallesTipoEvaluacionScreen> {
  List<dynamic> evaluaciones = [];
  bool isLoading = true;
  String? error;
  Map<String, dynamic>? tipoEvaluacion;
  Map<String, dynamic>? materia;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();

    final arguments =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;

    if (arguments != null) {
      tipoEvaluacion = arguments['tipo_evaluacion'] as Map<String, dynamic>;
      materia = arguments['materia'] as Map<String, dynamic>;
      _cargarEvaluaciones();
    } else {
      setState(() {
        error = 'No se encontraron datos';
        isLoading = false;
      });
    }
  }

  Future<void> _cargarEvaluaciones() async {
    if (tipoEvaluacion == null || materia == null) {
      setState(() {
        error = 'Faltan datos necesarios';
        isLoading = false;
      });
      return;
    }

    try {
      // Obtener ID del estudiante de sesión
      final usuario = await AuthService.getCurrentUser();
      if (usuario == null) {
        setState(() {
          error = 'No hay sesión activa';
          isLoading = false;
        });
        return;
      }

      final estudianteId = usuario.id.toString();
      final materiaId = materia!['id'].toString();
      final tipoEvaluacionId = tipoEvaluacion!['id'].toString();

      // MODIFICACIÓN: Añadir filtrado por año 2025
      final listaEvaluaciones =
          await EvaluacionesService.obtenerEvaluacionesPorEstudiante(
            estudianteId,
            materiaId: materiaId,
            anio: 2025, // Restaurar el filtro por año 2025
          );

      // Filtrar solo las evaluaciones del tipo seleccionado, sin filtrar por activo
      final evaluacionesFiltradas =
          listaEvaluaciones
              .where(
                (eval) =>
                    eval['tipo_evaluacion'] != null &&
                    eval['tipo_evaluacion']['id'].toString() ==
                        tipoEvaluacionId,
                // Incluir todos sin importar si están activos o no
              )
              .toList();

      // Verificar si hay evaluaciones y mostrar en consola para depuración
      AppLogger.i("Evaluaciones filtradas: ${evaluacionesFiltradas.length}");
      for (var eval in evaluacionesFiltradas) {
        AppLogger.d(
          "Evaluación: ${eval['titulo']} - Activo: ${eval['activo']} - ID: ${eval['id']}",
        );

        // Inspeccionar estructura completa de la evaluación para depurar
        if (eval['calificacion'] == null) {
          AppLogger.w(
            "Calificación nula para ${eval['titulo']}, buscando información adicional...",
          );
        } else {
          AppLogger.i(
            "Calificación encontrada: ${eval['calificacion']['nota']}",
          );
        }
      }

      // En _cargarEvaluaciones(), después de obtener los datos
      AppLogger.i(
        "✨ Obteniendo evaluaciones para estudiante: $estudianteId, materia: $materiaId",
      );

      // Depurar la primera evaluación completa para verificar su estructura
      if (evaluacionesFiltradas.isNotEmpty) {
        AppLogger.i("🔍 Primera evaluación (estructura completa):");
        final primeraEval = evaluacionesFiltradas.first;
        AppLogger.i(JsonEncoder.withIndent('  ').convert(primeraEval));
      }

      if (mounted) {
        setState(() {
          evaluaciones = evaluacionesFiltradas;
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
    if (tipoEvaluacion == null || materia == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: const Center(child: Text('Error: No se encontraron datos')),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('${tipoEvaluacion!['nombre']} - ${materia!['nombre']}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              setState(() {
                isLoading = true;
              });
              _cargarEvaluaciones();
            },
          ),
        ],
      ),
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : error != null
              ? _buildErrorState()
              : _buildEvaluacionesList(),
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
              });
              _cargarEvaluaciones();
            },
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildEvaluacionesList() {
    if (evaluaciones.isEmpty) {
      return _buildEmptyState(tipoEvaluacion!['nombre']);
    }

    return ListView.builder(
      itemCount: evaluaciones.length,
      padding: const EdgeInsets.all(16),
      itemBuilder: (context, index) {
        final evaluacion = evaluaciones[index];

        // Determinar color según estado
        Color statusColor;
        IconData statusIcon;
        String statusText;

        // Modificación: Mostrar calificación siempre que exista, sin importar publicación
        if (evaluacion['calificacion'] != null) {
          statusColor = Colors.green;
          statusIcon = Icons.check_circle;
          statusText = 'Calificado';
        } else if (evaluacion['publicado'] == true) {
          statusColor = Colors.blue;
          statusIcon = Icons.visibility;
          statusText = 'Publicado';
        } else {
          statusColor = Colors.orange;
          statusIcon = Icons.pending;
          statusText = 'No publicado';
        }

        return Card(
          margin: const EdgeInsets.only(bottom: 16),
          elevation: 3,
          child: ExpansionTile(
            leading: CircleAvatar(
              backgroundColor: statusColor.withAlpha(26),
              child: Icon(statusIcon, color: statusColor),
            ),
            title: Row(
              children: [
                Expanded(
                  child: Text(
                    evaluacion['titulo'],
                    style: const TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
                if (evaluacion['calificacion'] != null)
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getCalificacionColor(
                        evaluacion['calificacion'] != null
                            ? double.parse(
                              evaluacion['calificacion']['nota'].toString(),
                            )
                            : 0.0,
                        evaluacion['nota_maxima'] != null
                            ? double.parse(evaluacion['nota_maxima'].toString())
                            : 100.0,
                        evaluacion['nota_minima_aprobacion'] != null
                            ? double.parse(
                              evaluacion['nota_minima_aprobacion'].toString(),
                            )
                            : 51.0,
                      ),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${evaluacion['calificacion']['nota']}/${evaluacion['nota_maxima'] ?? 100.0}',
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
              ],
            ),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Fecha entrega: ${_formatFecha(evaluacion['fecha_entrega'])}',
                ),
                Text(
                  'Peso: ${evaluacion['porcentaje_nota_final']}% • Nota máxima: ${evaluacion['nota_maxima']}',
                ),
              ],
            ),
            trailing: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: statusColor.withAlpha(26),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                statusText,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: statusColor,
                ),
              ),
            ),
            children: [
              Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Descripción
                    if (evaluacion['descripcion'] != null &&
                        evaluacion['descripcion'].isNotEmpty)
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'Descripción:',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 4),
                            Text(evaluacion['descripcion']),
                          ],
                        ),
                      ),

                    const SizedBox(height: 16),

                    // Detalles de la evaluación
                    _buildEvaluacionDetails(evaluacion),

                    const SizedBox(height: 16),

                    // Información de calificación si existe
                    if (evaluacion['calificacion'] != null)
                      _buildCalificacionInfo(evaluacion['calificacion']),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildEmptyState(String tipoNombre) {
    String mensaje = 'evaluaciones';

    switch (tipoNombre.toUpperCase()) {
      case 'EXAMEN':
        mensaje = 'exámenes';
        break;
      case 'PRACTICOS':
        mensaje = 'prácticos';
        break;
      case 'TAREA':
        mensaje = 'tareas';
        break;
      // Puedes agregar más casos según sea necesario
    }

    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.assignment_outlined, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 16),
          Text(
            'No hay $mensaje registrados',
            style: TextStyle(fontSize: 18, color: Colors.grey[600]),
          ),
          const SizedBox(height: 8),
          Text(
            'Los $mensaje aparecerán aquí cuando el profesor los publique',
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }

  Widget _buildEvaluacionDetails(Map<String, dynamic> evaluacion) {
    // Determinar tipo de evaluación
    bool esParticipacion = evaluacion['tipo_objeto'] == 'participacion';

    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Información de la Evaluación',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          const SizedBox(height: 8),

          // Mostrar diferentes campos según el tipo de evaluación
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Primera columna
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Para participación mostrar fecha_registro, para otras mostrar fechas de entrega
                    esParticipacion
                        ? _buildDetalleRow(
                          Icons.calendar_today,
                          'Registro:',
                          _formatFecha(evaluacion['fecha_registro']),
                        )
                        : _buildDetalleRow(
                          Icons.calendar_today,
                          'Asignación:',
                          _formatFecha(evaluacion['fecha_asignacion']),
                        ),

                    // Solo mostrar fechas de entrega para evaluaciones no-participación
                    if (!esParticipacion) ...[
                      _buildDetalleRow(
                        Icons.event,
                        'Entrega:',
                        _formatFecha(evaluacion['fecha_entrega']),
                      ),
                      _buildDetalleRow(
                        Icons.timer,
                        'Límite:',
                        _formatFecha(evaluacion['fecha_limite']),
                      ),
                    ],
                  ],
                ),
              ),
              // Segunda columna
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildDetalleRow(
                      Icons.grade,
                      'Nota máx:',
                      '${evaluacion['nota_maxima'] ?? 100.0} pts',
                    ),
                    _buildDetalleRow(
                      Icons.check_circle,
                      'Aprob:',
                      '${evaluacion['nota_minima_aprobacion'] ?? 51.0} pts',
                    ),
                    _buildDetalleRow(
                      Icons.percent,
                      'Peso:',
                      '${evaluacion['porcentaje_nota_final']}%',
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 4),

          // Solo mostrar campos de entrega tardía para evaluaciones no-participación
          if (!esParticipacion)
            _buildDetalleRow(
              (evaluacion['permite_entrega_tardia'] ?? false)
                  ? Icons.check
                  : Icons.close,
              'Entrega tardía:',
              '${(evaluacion['permite_entrega_tardia'] ?? false) ? 'Sí' : 'No'}${(evaluacion['permite_entrega_tardia'] ?? false) ? ' (Penalización: ${evaluacion['penalizacion_tardio'] ?? 0}%)' : ''}',
            ),

          _buildDetalleRow(
            (evaluacion['publicado'] ?? false)
                ? Icons.visibility
                : Icons.visibility_off,
            'Estado:',
            (evaluacion['publicado'] ?? false) ? 'Publicado' : 'No publicado',
            color:
                (evaluacion['publicado'] ?? false)
                    ? Colors.green
                    : Colors.orange,
          ),
        ],
      ),
    );
  }

  Widget _buildDetalleRow(
    IconData icon,
    String label,
    String value, {
    Color? color,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4.0), // Reducido de 8.0
      child: Row(
        children: [
          Icon(
            icon,
            size: 14,
            color: color ?? Colors.grey[600],
          ), // Reducido de 16
          const SizedBox(width: 4), // Reducido de 8
          Expanded(
            child: RichText(
              text: TextSpan(
                style: DefaultTextStyle.of(
                  context,
                ).style.copyWith(fontSize: 13), // Tamaño reducido
                children: [
                  TextSpan(
                    text: '$label ',
                    style: TextStyle(
                      fontWeight: FontWeight.w500,
                      color: Colors.grey[700],
                    ),
                  ),
                  TextSpan(
                    text: value,
                    style: TextStyle(
                      color: color ?? Colors.grey[800],
                      fontWeight: color != null ? FontWeight.bold : null,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCalificacionInfo(Map<String, dynamic> calificacion) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: Colors.blue.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Tu Calificación',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
              color: Colors.blue,
            ),
          ),
          const SizedBox(height: 12),

          _buildDetalleRow(
            Icons.grade,
            'Nota:',
            '${calificacion['nota']}',
            color: Colors.blue[700],
          ),

          _buildDetalleRow(
            Icons.insights,
            'Nota final:',
            '${calificacion['nota_final']}',
            color: Colors.blue[700],
          ),

          if (calificacion['entrega_tardia'])
            _buildDetalleRow(
              Icons.timer_off,
              'Entrega tardía:',
              'Sí (-${calificacion['penalizacion_aplicada']}%)',
              color: Colors.orange[700],
            ),

          if (calificacion['fecha_entrega'] != null)
            _buildDetalleRow(
              Icons.calendar_today,
              'Fecha de entrega:',
              _formatFechaHora(calificacion['fecha_entrega']),
            ),

          if (calificacion['observaciones'] != null &&
              calificacion['observaciones'].isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Observaciones:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.all(8),
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(calificacion['observaciones']),
                  ),
                ],
              ),
            ),

          if (calificacion['retroalimentacion'] != null &&
              calificacion['retroalimentacion'].isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(top: 8.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Retroalimentación:',
                    style: TextStyle(fontWeight: FontWeight.w500),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    padding: const EdgeInsets.all(8),
                    width: double.infinity,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(calificacion['retroalimentacion']),
                  ),
                ],
              ),
            ),

          _buildDetalleRow(
            calificacion['finalizada'] ? Icons.check_circle : Icons.pending,
            'Estado:',
            calificacion['finalizada'] ? 'Finalizada' : 'Pendiente',
            color: calificacion['finalizada'] ? Colors.green : Colors.orange,
          ),
        ],
      ),
    );
  }

  Color _getCalificacionColor(
    double? nota,
    double? notaMaxima,
    double? notaMinimaAprobacion,
  ) {
    // Proporcionar valores predeterminados
    final notaSegura = nota ?? 0.0;
    final notaMaximaSegura = notaMaxima ?? 100.0;
    final notaMinimaAprobacionSegura = notaMinimaAprobacion ?? 51.0;

    // Calcular porcentaje de la nota sobre el total
    final porcentaje = (notaSegura / notaMaximaSegura) * 100;

    if (notaSegura < notaMinimaAprobacionSegura) {
      return Colors.red;
    } else if (porcentaje >= 90) {
      return Colors.green[700]!;
    } else if (porcentaje >= 80) {
      return Colors.lightGreen;
    } else if (porcentaje >= 70) {
      return Colors.amber[700]!;
    } else {
      return Colors.orange;
    }
  }

  String _formatFecha(String? fecha) {
    if (fecha == null) return 'No disponible';

    try {
      final DateTime dateTime = DateTime.parse(fecha);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    } catch (e) {
      return fecha;
    }
  }

  String _formatFechaHora(String? fecha) {
    if (fecha == null) return 'No disponible';

    try {
      final DateTime dateTime = DateTime.parse(fecha);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${_padZero(dateTime.minute)}';
    } catch (e) {
      return fecha;
    }
  }

  String _padZero(int number) {
    return number.toString().padLeft(2, '0');
  }
}

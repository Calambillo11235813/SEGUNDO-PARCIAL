import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/tutor/tutor_service.dart';
import 'package:aplicacion_movil/services/tutor/filtros_service.dart';
import 'package:aplicacion_movil/services/auth_service.dart'; // Agregar import
import 'package:aplicacion_movil/utils/logger.dart';

class CalificacionesEstudianteScreen extends StatefulWidget {
  final Map<String, dynamic> estudiante;
  final String anioAcademico;

  const CalificacionesEstudianteScreen({
    super.key,
    required this.estudiante,
    required this.anioAcademico,
  });

  @override
  State<CalificacionesEstudianteScreen> createState() =>
      _CalificacionesEstudianteScreenState();
}

class _CalificacionesEstudianteScreenState
    extends State<CalificacionesEstudianteScreen> {
  bool _isLoading = true;
  List<dynamic> _trimestres = [];
  int? _selectedTrimestreId;
  Map<String, dynamic>? _calificaciones;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadTrimestres();
  }

  Future<void> _loadTrimestres() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      List<Map<String, dynamic>> trimestres = [];

      try {
        // Intentar cargar trimestres desde el servidor
        trimestres = await FiltrosTutorService.obtenerTrimestresPorAnio(
          widget.anioAcademico,
        );
      } catch (e) {
        // Si falla, usar datos de ejemplo
        AppLogger.w(
          "Error obteniendo trimestres: $e. Usando datos predefinidos.",
        );
        trimestres = [
          {
            'id': 1,
            'nombre': 'Primer Trimestre',
            'fecha_inicio': '${widget.anioAcademico}-01-15',
            'fecha_fin': '${widget.anioAcademico}-04-15',
          },
          {
            'id': 2,
            'nombre': 'Segundo Trimestre',
            'fecha_inicio': '${widget.anioAcademico}-05-01',
            'fecha_fin': '${widget.anioAcademico}-08-15',
          },
          {
            'id': 3,
            'nombre': 'Tercer Trimestre',
            'fecha_inicio': '${widget.anioAcademico}-09-01',
            'fecha_fin': '${widget.anioAcademico}-12-15',
          },
        ];
      }

      setState(() {
        _trimestres = trimestres;
        if (trimestres.isNotEmpty) {
          // Seleccionar el primer trimestre por defecto
          _selectedTrimestreId = trimestres[0]['id'];
          _loadCalificaciones();
        } else {
          _isLoading = false;
        }
      });
    } catch (e) {
      AppLogger.e("Error cargando trimestres", e);
      setState(() {
        _error = "Error al cargar trimestres: $e";
        _isLoading = false;
      });
    }
  }

  /// ✅ AGREGAR: Método helper para extraer materias de cualquier estructura
  List<dynamic> _extractMaterias(Map<String, dynamic> response) {
    // Prioridad 1: Materias en objeto estudiante
    if (response['estudiante'] != null &&
        response['estudiante']['materias'] != null &&
        response['estudiante']['materias'] is List) {
      AppLogger.d('Materias encontradas en estudiante.materias');
      return response['estudiante']['materias'] as List<dynamic>;
    }

    // Prioridad 2: Materias en la raíz
    if (response['materias'] != null && response['materias'] is List) {
      AppLogger.d('Materias encontradas en raíz');
      return response['materias'] as List<dynamic>;
    }

    // Prioridad 3: Buscar en otros posibles lugares
    if (response['data'] != null &&
        response['data']['materias'] != null &&
        response['data']['materias'] is List) {
      AppLogger.d('Materias encontradas en data.materias');
      return response['data']['materias'] as List<dynamic>;
    }

    AppLogger.w('No se encontraron materias en ninguna ubicación conocida');
    return <dynamic>[];
  }

  Future<void> _loadCalificaciones() async {
    if (_selectedTrimestreId == null) return;

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Validación segura del tutor
      final tutorId = await AuthService.getCurrentUserId();
      if (tutorId == null) {
        throw Exception('No se pudo obtener el ID del tutor autenticado');
      }

      final userRole = await AuthService.getCurrentUserRole();
      if (userRole != 'Tutor') {
        throw Exception('El usuario actual no tiene permisos de tutor');
      }

      AppLogger.d('Tutor autenticado - ID: $tutorId, Rol: $userRole');

      // Validación de datos del estudiante
      final estudianteId = widget.estudiante['id'];
      if (estudianteId == null) {
        throw Exception('ID de estudiante no válido');
      }

      // Obtener calificaciones del estudiante
      final response =
          await TutorService.obtenerCalificacionesEstudianteDetalle(
            tutorId,
            estudianteId is int
                ? estudianteId
                : int.tryParse(estudianteId.toString()) ?? 0,
            anioAcademico: widget.anioAcademico,
            trimestreId: _selectedTrimestreId,
          );

      AppLogger.d('Respuesta del servicio: $response');

      // ✅ USAR EL MÉTODO HELPER
      final materias = _extractMaterias(response);

      // Crear objeto de calificaciones normalizado
      final calificaciones = <String, dynamic>{
        'tutor': response['tutor'],
        'estudiante': response['estudiante'],
        'materias': materias,
      };

      AppLogger.i('Total de materias procesadas: ${materias.length}');

      setState(() {
        _calificaciones = calificaciones;
        _isLoading = false;
      });
    } catch (e, stackTrace) {
      AppLogger.e(
        "Error cargando calificaciones del estudiante",
        e,
        stackTrace,
      );
      setState(() {
        _error = "Error al cargar calificaciones: $e";
        _isLoading = false;
      });
    }
  }

  // ✅ AGREGAR: Método helper para validar datos
  bool _hasCalificacionesData() {
    return _calificaciones != null &&
        _calificaciones!['materias'] != null &&
        _calificaciones!['materias'] is List &&
        (_calificaciones!['materias'] as List).isNotEmpty;
  }

  /// ✅ AGREGAR: Método para calcular promedio real de la materia
  double _calcularPromedioMateria(Map<String, dynamic> materia) {
    final evaluaciones = materia['evaluaciones'] as List?;

    if (evaluaciones == null || evaluaciones.isEmpty) {
      return 0.0;
    }

    double sumaTotal = 0.0;
    double pesoTotal = 0.0;
    int evaluacionesConNota = 0;

    for (final evaluacion in evaluaciones) {
      if (evaluacion != null && evaluacion['calificacion'] != null) {
        final calificacion = evaluacion['calificacion'];
        final nota =
            (calificacion['nota_final'] as num?)?.toDouble() ??
            (calificacion['nota'] as num?)?.toDouble();
        final porcentaje =
            (calificacion['porcentaje'] as num?)?.toDouble() ?? 1.0;

        if (nota != null && nota > 0) {
          sumaTotal += (nota * porcentaje);
          pesoTotal += porcentaje;
          evaluacionesConNota++;
        }
      }
    }

    if (pesoTotal > 0) {
      return sumaTotal / pesoTotal;
    } else if (evaluacionesConNota > 0) {
      // Si no hay porcentajes, usar promedio simple
      double suma = 0.0;
      for (final evaluacion in evaluaciones) {
        if (evaluacion != null && evaluacion['calificacion'] != null) {
          final calificacion = evaluacion['calificacion'];
          final nota =
              (calificacion['nota_final'] as num?)?.toDouble() ??
              (calificacion['nota'] as num?)?.toDouble();
          if (nota != null && nota > 0) {
            suma += nota;
          }
        }
      }
      return suma / evaluacionesConNota;
    }

    return 0.0;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Calificaciones - ${widget.estudiante['nombre']}'),
      ),
      body: Column(
        children: [
          // Información del estudiante
          _buildEstudianteInfo(),

          // Selector de trimestre
          _buildTrimestreSelector(),

          // Contenido principal
          Expanded(
            child:
                _isLoading
                    ? const Center(child: CircularProgressIndicator())
                    : _error != null
                    ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(
                            _error!,
                            style: const TextStyle(color: Colors.red),
                            textAlign: TextAlign.center,
                          ),
                          const SizedBox(height: 16),
                          ElevatedButton(
                            onPressed: _loadCalificaciones,
                            child: const Text('Reintentar'),
                          ),
                        ],
                      ),
                    )
                    // ✅ USAR EL MÉTODO HELPER
                    : !_hasCalificacionesData()
                    ? const Center(
                      child: Text('No hay calificaciones disponibles'),
                    )
                    : _buildCalificacionesList(),
          ),
        ],
      ),
    );
  }

  Widget _buildEstudianteInfo() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: AppTheme.primaryColorLight,
      child: Row(
        children: [
          CircleAvatar(
            radius: 30,
            backgroundColor: AppTheme.primaryColor,
            child: Text(
              '${widget.estudiante['nombre'][0]}${widget.estudiante['apellido'][0]}',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 18,
              ),
            ),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${widget.estudiante['nombre']} ${widget.estudiante['apellido']}',
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Código: ${widget.estudiante['codigo']}',
                  style: const TextStyle(fontSize: 14),
                ),
                Text(
                  'Año académico: ${widget.anioAcademico}',
                  style: const TextStyle(fontSize: 14),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTrimestreSelector() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      color: Colors.grey[100],
      child:
          _trimestres.isEmpty
              ? const Center(child: Text('No hay trimestres disponibles'))
              : SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                child: Row(
                  children:
                      _trimestres.map((trimestre) {
                        final isSelected =
                            trimestre['id'] == _selectedTrimestreId;
                        return Padding(
                          padding: const EdgeInsets.only(right: 8),
                          child: ChoiceChip(
                            label: Text(trimestre['nombre']),
                            selected: isSelected,
                            selectedColor: AppTheme.primaryColorLight,
                            onSelected: (_) {
                              setState(() {
                                _selectedTrimestreId = trimestre['id'];
                                _loadCalificaciones();
                              });
                            },
                          ),
                        );
                      }).toList(),
                ),
              ),
    );
  }

  Widget _buildCalificacionesList() {
    // ✅ DEBUGGING MEJORADO
    AppLogger.d('=== DEBUG CALIFICACIONES ===');
    AppLogger.d('_calificaciones keys: ${_calificaciones?.keys}');

    if (_calificaciones?['estudiante'] != null) {
      AppLogger.d('estudiante keys: ${_calificaciones!['estudiante'].keys}');
    }

    if (_calificaciones?['materias'] != null) {
      AppLogger.d('materias length: ${_calificaciones!['materias'].length}');
      AppLogger.d('materias type: ${_calificaciones!['materias'].runtimeType}');
    }

    // ✅ VALIDACIÓN SEGURA ANTES DE USAR LOS DATOS
    if (_calificaciones == null) {
      return const Center(
        child: Text('No hay datos de calificaciones disponibles'),
      );
    }

    final materias = _calificaciones!['materias'];

    // ✅ VERIFICAR QUE SEA UNA LISTA
    if (materias is! List) {
      AppLogger.w(
        'Los datos de materias no son una lista: ${materias.runtimeType}',
      );
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: Colors.orange),
            const SizedBox(height: 16),
            const Text('Formato de datos incorrecto'),
            const SizedBox(height: 8),
            Text('Tipo: ${materias.runtimeType}'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _loadCalificaciones,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    // ✅ VERIFICAR QUE NO ESTÉ VACÍA
    if (materias.isEmpty) {
      return const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.school_outlined, size: 64, color: Colors.grey),
            SizedBox(height: 16),
            Text('No hay materias registradas para este trimestre'),
          ],
        ),
      );
    }

    AppLogger.i('Construyendo lista con ${materias.length} materias');

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: materias.length,
      itemBuilder: (context, index) {
        final materia = materias[index];
        AppLogger.d('Procesando materia $index: ${materia?['nombre']}');

        // ✅ VALIDACIÓN ADICIONAL POR ITEM
        if (materia == null) {
          return Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Text('Datos de materia no válidos (índice: $index)'),
            ),
          );
        }

        // ✅ USAR EL PROMEDIO CALCULADO
        final double promedio = _calcularPromedioMateria(materia);

        return Card(
          margin: const EdgeInsets.only(bottom: 12),
          elevation: 2,
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
                        materia['nombre']?.toString() ?? 'Sin nombre',
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: _getColorForCalificacion(promedio),
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: Text(
                        promedio.toStringAsFixed(1),
                        style: const TextStyle(
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 8),

                // ✅ AGREGAR: Mostrar cantidad de evaluaciones
                Text(
                  'Evaluaciones: ${(materia['evaluaciones'] as List?)?.length ?? 0}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),

                const Divider(),
                const SizedBox(height: 4),
                _buildEvaluacionesList(materia['evaluaciones'] as List? ?? []),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEvaluacionesList(List? evaluaciones) {
    // ✅ DEBUGGING PARA EVALUACIONES
    AppLogger.d('=== DEBUG EVALUACIONES ===');
    AppLogger.d('Total evaluaciones: ${evaluaciones?.length ?? 0}');

    if (evaluaciones != null && evaluaciones.isNotEmpty) {
      final primeraEvaluacion = evaluaciones[0];
      AppLogger.d('Primera evaluación keys: ${primeraEvaluacion?.keys}');
      if (primeraEvaluacion?['calificacion'] != null) {
        AppLogger.d(
          'Calificación keys: ${primeraEvaluacion['calificacion'].keys}',
        );
        AppLogger.d('Nota: ${primeraEvaluacion['calificacion']['nota']}');
        AppLogger.d(
          'Nota final: ${primeraEvaluacion['calificacion']['nota_final']}',
        );
      }
    }

    // ✅ VALIDACIÓN SEGURA DE LA LISTA
    if (evaluaciones == null || evaluaciones.isEmpty) {
      return const Text('No hay evaluaciones registradas');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          evaluaciones.where((evaluacion) => evaluacion != null).map((
            evaluacion,
          ) {
            AppLogger.d('Procesando evaluación: ${evaluacion['titulo']}');

            // ✅ CORRECCIÓN: Acceder a la nota desde el objeto calificacion
            double nota = 0.0;
            String fechaTexto = 'No registrada';
            String estadoTexto = '';

            if (evaluacion['calificacion'] != null) {
              final calificacion = evaluacion['calificacion'];
              nota =
                  (calificacion['nota_final'] as num?)?.toDouble() ??
                  (calificacion['nota'] as num?)?.toDouble() ??
                  0.0;

              AppLogger.d('Nota extraída: $nota para ${evaluacion['titulo']}');

              // Estado de la calificación
              if (calificacion['finalizada'] == true) {
                estadoTexto = '✓ Finalizada';
              } else {
                estadoTexto = '⏳ Pendiente';
              }
            } else {
              AppLogger.w('No hay calificación para: ${evaluacion['titulo']}');
              estadoTexto = '❌ Sin calificar';
            }

            // Manejar fecha según el tipo de evaluación
            if (evaluacion['fecha_registro'] != null) {
              fechaTexto = _formatearFecha(
                evaluacion['fecha_registro'].toString(),
              );
            } else if (evaluacion['fecha_entrega'] != null) {
              fechaTexto = _formatearFecha(
                evaluacion['fecha_entrega'].toString(),
              );
            } else if (evaluacion['fecha_asignacion'] != null) {
              fechaTexto = _formatearFecha(
                evaluacion['fecha_asignacion'].toString(),
              );
            }

            return Card(
              margin: const EdgeInsets.only(bottom: 6),
              elevation: 1,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            evaluacion['titulo']?.toString() ?? 'Sin título',
                            style: const TextStyle(
                              fontWeight: FontWeight.w600,
                              fontSize: 14,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            fechaTexto,
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[600],
                            ),
                          ),
                          // ✅ AGREGAR: Información adicional
                          Row(
                            children: [
                              if (evaluacion['tipo_evaluacion'] != null)
                                Container(
                                  padding: const EdgeInsets.symmetric(
                                    horizontal: 6,
                                    vertical: 2,
                                  ),
                                  margin: const EdgeInsets.only(
                                    top: 4,
                                    right: 8,
                                  ),
                                  decoration: BoxDecoration(
                                    color: Colors.blue[100],
                                    borderRadius: BorderRadius.circular(8),
                                  ),
                                  child: Text(
                                    evaluacion['tipo_evaluacion']['nombre'] ??
                                        'N/A',
                                    style: TextStyle(
                                      fontSize: 10,
                                      color: Colors.blue[800],
                                      fontWeight: FontWeight.w500,
                                    ),
                                  ),
                                ),
                              Text(
                                estadoTexto,
                                style: TextStyle(
                                  fontSize: 10,
                                  color:
                                      estadoTexto.contains('✓')
                                          ? Colors.green[700]
                                          : Colors.orange[700],
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: 12,
                        vertical: 6,
                      ),
                      decoration: BoxDecoration(
                        color: _getColorForCalificacion(nota),
                        borderRadius: BorderRadius.circular(12),
                      ),
                      child: Text(
                        nota.toStringAsFixed(1),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                          fontSize: 14,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
    );
  }

  // ✅ AGREGAR: Método para formatear fechas
  String _formatearFecha(String fecha) {
    try {
      final dateTime = DateTime.parse(fecha);
      return '${dateTime.day}/${dateTime.month}/${dateTime.year}';
    } catch (e) {
      return fecha.substring(0, fecha.length > 10 ? 10 : fecha.length);
    }
  }

  Color _getColorForCalificacion(double nota) {
    if (nota >= 17) return Colors.green[700]!;
    if (nota >= 14) return Colors.blue[700]!;
    if (nota >= 10.5) return Colors.amber[800]!;
    return Colors.red[700]!;
  }
}

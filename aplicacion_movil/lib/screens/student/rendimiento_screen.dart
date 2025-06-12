import 'package:flutter/material.dart';
import '../../services/estudiante/historial_service.dart';
import '../../services/estudiante/prediccion_service.dart';
// ignore: unused_import
import '../../utils/logger.dart';
import '../../widgets/student_drawer.dart';

class RendimientoScreen extends StatefulWidget {
  final int estudianteId;
  final String? estudianteCodigo;

  const RendimientoScreen({
    required this.estudianteId,
    this.estudianteCodigo,
    Key? key,
  }) : super(key: key);

  @override
  State<RendimientoScreen> createState() => _RendimientoScreenState();
}

class _RendimientoScreenState extends State<RendimientoScreen> {
  bool _isLoading = true;
  String? _error;
  List<dynamic> _historial = [];
  final Map<String, dynamic> _predicciones = {}; // key: "materiaId-trimestreId"

  // Filtros
  List<int> _anios = [];
  Map<int, List<dynamic>> _trimestresPorAnio = {};
  int? _anioSeleccionado;
  dynamic _trimestreSeleccionado;

  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // 1. Cargar historial académico
      final historialData = await HistorialService.obtenerHistorialAcademico(
        widget.estudianteId,
      );

      if (historialData == null) {
        setState(() {
          _error = "No se pudo cargar el historial académico";
          _isLoading = false;
        });
        return;
      }

      // 2. Procesar datos del historial
      _historial = historialData['historial'] ?? [];

      // Extraer años académicos únicos
      _anios =
          _historial
              .map<int>((trimestre) => trimestre['año_academico'] as int)
              .toSet()
              .toList()
            ..sort((a, b) => b.compareTo(a)); // Orden descendente

      // Agrupar trimestres por año
      _trimestresPorAnio = {};
      for (var trimestre in _historial) {
        final anio = trimestre['año_academico'] as int;
        if (!_trimestresPorAnio.containsKey(anio)) {
          _trimestresPorAnio[anio] = [];
        }
        _trimestresPorAnio[anio]!.add(trimestre);
      }

      // Establecer valores iniciales de filtro
      if (_anios.isNotEmpty) {
        _anioSeleccionado = _anios.first;
        if (_trimestresPorAnio[_anioSeleccionado]!.isNotEmpty) {
          _trimestreSeleccionado = _trimestresPorAnio[_anioSeleccionado]!.first;
        }
      }

      setState(() {
        _isLoading = false;
      });

      // 3. Generar predicciones (después de actualizar UI con datos básicos)
      await _generarPredicciones();
    } catch (e) {
      setState(() {
        _error = "Error al cargar datos: $e";
        _isLoading = false;
      });
    }
  }

  Future<void> _generarPredicciones() async {
    if (_historial.isEmpty) return;

    // Para cada trimestre y materia, generar predicción
    for (var trimestre in _historial) {
      for (var materia in trimestre['materias']) {
        final key = "${materia['id']}-${trimestre['id']}";

        try {
          final prediccion = await PrediccionService.predecirRendimiento(
            promedioNotasAnterior: _castToDouble(materia['promedio_nota']) ?? 0,
            porcentajeAsistencia:
                _castToDouble(materia['porcentaje_asistencia']) ?? 0,
            promedioParticipaciones:
                _castToDouble(materia['promedio_participacion']) ?? 0,
            materiasCursadas:
                1, // Asumimos que el estudiante está cursando esta materia
            evaluacionesCompletadas: materia['total_clases'] ?? 0,
            estudianteCodigo: widget.estudianteCodigo,
          );

          if (prediccion != null) {
            setState(() {
              _predicciones[key] = prediccion;
            });
          }
        } catch (e) {
          print("Error generando predicción para $key: $e");
        }
      }
    }
  }

  // Utilidad para convertir valores a double de forma segura
  double? _castToDouble(dynamic value) {
    if (value == null) return null;
    if (value is double) return value;
    if (value is int) return value.toDouble();
    if (value is String) return double.tryParse(value);
    return null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Rendimiento Académico'), elevation: 2),
      drawer:
          // ignore: unnecessary_null_comparison
          widget.estudianteId != null
              ? StudentDrawer(
                currentUser: null, // Deberías pasar el usuario actual aquí
                currentRoute: '/student/rendimiento',
              )
              : null,
      body: _buildBody(),
    );
  }

  Widget _buildBody() {
    if (_isLoading) {
      return const Center(child: CircularProgressIndicator());
    }

    if (_error != null) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.error_outline, size: 48, color: Colors.red),
            const SizedBox(height: 16),
            Text(_error!, style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _cargarDatos,
              child: const Text('Reintentar'),
            ),
          ],
        ),
      );
    }

    if (_historial.isEmpty) {
      return const Center(
        child: Text(
          'No hay datos de rendimiento académico disponibles',
          style: TextStyle(fontSize: 16),
        ),
      );
    }

    return Column(
      children: [
        // Filtros de año y trimestre
        _buildFilters(),

        // Lista de materias del trimestre seleccionado
        Expanded(
          child:
              _trimestreSeleccionado != null
                  ? _buildMateriasList(_trimestreSeleccionado)
                  : const Center(child: Text('Seleccione un trimestre')),
        ),
      ],
    );
  }

  Widget _buildFilters() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Row(
        children: [
          // Filtro de año académico
          Expanded(
            child: DropdownButtonFormField<int>(
              decoration: const InputDecoration(
                labelText: 'Año Académico',
                border: OutlineInputBorder(),
              ),
              value: _anioSeleccionado,
              items:
                  _anios.map((anio) {
                    return DropdownMenuItem<int>(
                      value: anio,
                      child: Text('$anio'),
                    );
                  }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _anioSeleccionado = value;
                    _trimestreSeleccionado = _trimestresPorAnio[value]?.first;
                  });
                }
              },
            ),
          ),
          const SizedBox(width: 16),

          // Filtro de trimestre
          Expanded(
            child: DropdownButtonFormField<dynamic>(
              decoration: const InputDecoration(
                labelText: 'Trimestre',
                border: OutlineInputBorder(),
              ),
              value: _trimestreSeleccionado,
              items:
                  _anioSeleccionado != null
                      ? _trimestresPorAnio[_anioSeleccionado]!.map((trimestre) {
                        return DropdownMenuItem<dynamic>(
                          value: trimestre,
                          child: Text(trimestre['nombre']),
                        );
                      }).toList()
                      : [],
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _trimestreSeleccionado = value;
                  });
                }
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMateriasList(dynamic trimestre) {
    final materias = trimestre['materias'] as List;

    if (materias.isEmpty) {
      return const Center(child: Text('No hay materias para este trimestre'));
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 8),
      itemCount: materias.length,
      itemBuilder: (context, index) {
        final materia = materias[index];
        final key = "${materia['id']}-${trimestre['id']}";
        final prediccion = _predicciones[key];

        return Card(
          margin: const EdgeInsets.symmetric(vertical: 8, horizontal: 4),
          elevation: 3,
          child: ExpansionTile(
            title: Text(
              materia['nombre'],
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            subtitle: Text('Promedio: ${materia['promedio_nota'] ?? "N/A"}'),
            children: [
              // Detalles de la materia
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Estadísticas de la materia
                    _buildStatisticRow(
                      'Notas',
                      materia['promedio_nota']?.toString() ?? 'N/A',
                      Icons.star,
                      Colors.amber,
                    ),
                    _buildStatisticRow(
                      'Participación',
                      materia['promedio_participacion']?.toString() ?? 'N/A',
                      Icons.record_voice_over,
                      Colors.blue,
                    ),
                    _buildStatisticRow(
                      'Asistencia',
                      '${materia['porcentaje_asistencia']?.toString() ?? 'N/A'}%',
                      Icons.calendar_today,
                      Colors.green,
                    ),
                    _buildStatisticRow(
                      'Clases asistidas',
                      '${materia['asistencias_presentes'] ?? 0}/${materia['total_clases'] ?? 0}',
                      Icons.people,
                      Colors.purple,
                    ),
                    const Divider(height: 32),

                    // Predicción
                    if (prediccion != null) ...[
                      const Text(
                        'Predicción de Rendimiento',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 8),

                      // Rendimiento predicho
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: _getPrediccionColor(
                            prediccion['prediccion']['categoria'],
                          ).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(
                            color: _getPrediccionColor(
                              prediccion['prediccion']['categoria'],
                            ),
                            width: 1,
                          ),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(
                                  _getPrediccionIcon(
                                    prediccion['prediccion']['categoria'],
                                  ),
                                  color: _getPrediccionColor(
                                    prediccion['prediccion']['categoria'],
                                  ),
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  'Rendimiento esperado: ${prediccion['prediccion']['rendimiento_predicho']} - ${prediccion['prediccion']['categoria']}',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: _getPrediccionColor(
                                      prediccion['prediccion']['categoria'],
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            Text(
                              'Nivel de confianza: ${prediccion['prediccion']['nivel_confianza']}%',
                            ),

                            // Recomendaciones
                            if (prediccion['prediccion']['recomendaciones'] !=
                                null) ...[
                              const SizedBox(height: 16),
                              const Text(
                                'Recomendaciones:',
                                style: TextStyle(fontWeight: FontWeight.bold),
                              ),
                              const SizedBox(height: 8),
                              ...(prediccion['prediccion']['recomendaciones']
                                      as List)
                                  .map<Widget>((recomendacion) {
                                    return Padding(
                                      padding: const EdgeInsets.only(
                                        bottom: 8.0,
                                      ),
                                      child: Row(
                                        crossAxisAlignment:
                                            CrossAxisAlignment.start,
                                        children: [
                                          const Icon(
                                            Icons.lightbulb_outline,
                                            size: 18,
                                            color: Colors.amber,
                                          ),
                                          const SizedBox(width: 8),
                                          Expanded(
                                            child: Text(
                                              recomendacion['mensaje'] ?? '',
                                            ),
                                          ),
                                        ],
                                      ),
                                    );
                                  })
                                  .toList(),
                            ],
                          ],
                        ),
                      ),
                    ] else ...[
                      // Si no hay predicción, mostrar un mensaje
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 16),
                        child: Text(
                          'Generando predicción...',
                          style: TextStyle(
                            fontStyle: FontStyle.italic,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }

  Widget _buildStatisticRow(
    String label,
    String value,
    IconData icon,
    Color color,
  ) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 8),
          Text('$label:', style: const TextStyle(fontWeight: FontWeight.w500)),
          const Spacer(),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
              border: Border.all(color: color.withOpacity(0.3)),
            ),
            child: Text(
              value,
              style: TextStyle(
                color: color.withOpacity(0.8),
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getPrediccionColor(String categoria) {
    switch (categoria.toLowerCase()) {
      case 'excelente':
        return Colors.green;
      case 'bueno':
        return Colors.lightGreen;
      case 'regular':
        return Colors.orange;
      case 'bajo':
        return Colors.red;
      default:
        return Colors.blue;
    }
  }

  IconData _getPrediccionIcon(String categoria) {
    switch (categoria.toLowerCase()) {
      case 'excelente':
        return Icons.emoji_events;
      case 'bueno':
        return Icons.thumb_up;
      case 'regular':
        return Icons.thumbs_up_down;
      case 'bajo':
        return Icons.warning;
      default:
        return Icons.insights;
    }
  }
}

import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/tutor/tutor_service.dart';
import 'package:aplicacion_movil/services/tutor/filtros_service.dart';
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

  Future<void> _loadCalificaciones() async {
    if (_selectedTrimestreId == null) return;

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Obtener ID del tutor (se podría pasar como parámetro desde pantalla anterior)
      final tutorId = 1; // Asumiendo un valor por defecto para desarrollo

      // Obtener calificaciones del estudiante
      final calificaciones =
          await TutorService.obtenerCalificacionesEstudianteDetalle(
            tutorId,
            widget.estudiante['id'],
            anioAcademico: widget.anioAcademico,
            trimestreId: _selectedTrimestreId,
          );

      setState(() {
        _calificaciones = calificaciones;
        _isLoading = false;
      });
    } catch (e) {
      AppLogger.e("Error cargando calificaciones del estudiante", e);
      setState(() {
        _error = "Error al cargar calificaciones: $e";
        _isLoading = false;
      });
    }
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
                    : _calificaciones == null ||
                        (_calificaciones!['materias'] as List).isEmpty
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
    final materias = _calificaciones!['materias'] as List;

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: materias.length,
      itemBuilder: (context, index) {
        final materia = materias[index];
        final double promedio = materia['promedio'] ?? 0.0;

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
                        materia['nombre'],
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
                const Divider(),
                const SizedBox(height: 4),
                _buildEvaluacionesList(materia['evaluaciones'] as List),
              ],
            ),
          ),
        );
      },
    );
  }

  Widget _buildEvaluacionesList(List evaluaciones) {
    if (evaluaciones.isEmpty) {
      return const Text('No hay evaluaciones registradas');
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children:
          evaluaciones.map((evaluacion) {
            final double nota = evaluacion['nota'] ?? 0.0;

            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          evaluacion['nombre'],
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                        Text(
                          'Fecha: ${evaluacion['fecha'] ?? 'No registrada'}',
                          style: TextStyle(
                            fontSize: 12,
                            color: Colors.grey[600],
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: _getColorForCalificacion(nota).withOpacity(0.2),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      nota.toStringAsFixed(1),
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: _getColorForCalificacion(nota),
                      ),
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
    );
  }

  Color _getColorForCalificacion(double nota) {
    if (nota >= 17) return Colors.green[700]!;
    if (nota >= 14) return Colors.blue[700]!;
    if (nota >= 10.5) return Colors.amber[800]!;
    return Colors.red[700]!;
  }
}

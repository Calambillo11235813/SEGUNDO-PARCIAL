import 'package:flutter/material.dart';
import 'package:aplicacion_movil/utils/logger.dart';
import 'package:aplicacion_movil/services/estudiante/trimestre_service.dart';

class CalificacionesMateriaScreen extends StatefulWidget {
  const CalificacionesMateriaScreen({super.key});

  @override
  State<CalificacionesMateriaScreen> createState() =>
      _CalificacionesMateriaScreenState();
}

class _CalificacionesMateriaScreenState
    extends State<CalificacionesMateriaScreen> {
  final TrimestreService _trimestreService = TrimestreService();
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic>? _datos;
  int estudianteId = 0; // Nueva variable

  @override
  void initState() {
    super.initState();
    // Retrasamos la carga para asegurar que el contexto está disponible
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _cargarCalificaciones();
    });
  }

  Future<void> _cargarCalificaciones() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final arguments =
          ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;

      if (arguments == null) {
        setState(() {
          _error = "No se recibieron parámetros";
          _isLoading = false;
        });
        return;
      }

      final int estudianteIdArg = arguments['estudianteId'] as int? ?? 0;
      final int trimestreId = arguments['trimestreId'] as int? ?? 0;

      // Guardar el ID del estudiante
      estudianteId = estudianteIdArg;

      if (estudianteId == 0 || trimestreId == 0) {
        setState(() {
          _error = "ID de estudiante o trimestre no válido";
          _isLoading = false;
        });
        return;
      }

      AppLogger.d(
        "Cargando calificaciones para estudiante $estudianteId, trimestre $trimestreId",
      );

      setState(() {
        _isLoading = true;
        _error = null;
      });

      try {
        // Intentar cargar datos reales del API
        final datos = await _trimestreService.obtenerCalificacionesTrimestre(
          estudianteId,
          trimestreId,
        );

        setState(() {
          _datos = datos;
          _isLoading = false;
        });
      } catch (e) {
        AppLogger.e("Error en la llamada al API", e);
        setState(() {
          _error = "Error obteniendo información: $e";
          _isLoading = false;
          _datos = null;
        });
      }
    } catch (e) {
      AppLogger.e("Error cargando calificaciones", e);
      setState(() {
        _error = "Error obteniendo información: $e";
        _isLoading = false;
        _datos = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    if (_error != null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Error')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Padding(
                padding: const EdgeInsets.all(20.0),
                child: Text(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _cargarCalificaciones,
                child: const Text('Reintentar carga'),
              ),
            ],
          ),
        ),
      );
    }

    // Verificar que _datos no es null antes de acceder a sus propiedades
    if (_datos == null) {
      return Scaffold(
        appBar: AppBar(title: const Text('Calificaciones')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text(
                'No se pudieron cargar los datos',
                style: TextStyle(fontSize: 16),
              ),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: _cargarCalificaciones,
                child: const Text('Reintentar carga'),
              ),
            ],
          ),
        ),
      );
    }

    // Extraer información del trimestre con seguridad contra null
    final trimestre = _datos!['trimestre'] as Map<String, dynamic>?;
    final nombreTrimestre = trimestre?['nombre'] as String? ?? 'Trimestre';

    // Extraer las materias con seguridad contra null
    final List<dynamic> materias = _datos!['materias'] as List<dynamic>? ?? [];

    return Scaffold(
      appBar: AppBar(title: Text(nombreTrimestre)),
      body:
          materias.isEmpty
              ? const Center(
                child: Text(
                  'No hay calificaciones disponibles para este trimestre',
                ),
              )
              : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: materias.length,
                itemBuilder: (context, index) {
                  final materia = materias[index] as Map<String, dynamic>;
                  final double promedio =
                      (materia['promedio'] as num?)?.toDouble() ?? 0.0;
                  final String nombreMateria =
                      materia['nombre'] as String? ?? 'Sin nombre';

                  return Card(
                    margin: const EdgeInsets.only(bottom: 16),
                    elevation: 2,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: BorderSide(
                        color:
                            promedio >= 51 ? Colors.green : Colors.red.shade300,
                        width: 1,
                      ),
                    ),
                    // Agregar InkWell para detectar taps
                    child: InkWell(
                      // Agregar esta función onTap
                      onTap: () {
                        // Navegar a la pantalla de evaluaciones con el ID de materia
                        Navigator.pushNamed(
                          context,
                          '/student/materia/evaluaciones',
                          arguments: {
                            'materia': {
                              'id': materia['id'],
                              'nombre': nombreMateria,
                            },
                            'anio':
                                int.tryParse(
                                  _datos?['trimestre']?['año_academico']
                                          ?.toString() ??
                                      "2025",
                                ) ??
                                2025,
                          },
                        );
                      },
                      borderRadius: BorderRadius.circular(12),
                      child: Padding(
                        padding: const EdgeInsets.all(16.0),
                        child: Row(
                          children: [
                            Expanded(
                              child: Text(
                                nombreMateria,
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w500,
                                  color: Theme.of(context).primaryColor,
                                ),
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 8,
                              ),
                              decoration: BoxDecoration(
                                // Reemplazar esto:
                                // color: promedio >= 51 ? Colors.green.withOpacity(0.2) : Colors.red.withOpacity(0.2),

                                // Con esto:
                                color: (promedio >= 51
                                        ? Colors.green
                                        : Colors.red)
                                    .withAlpha(51),
                                borderRadius: BorderRadius.circular(20),
                              ),
                              child: Text(
                                promedio.toStringAsFixed(0),
                                style: TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                  color:
                                      promedio >= 51
                                          ? Colors.green
                                          : Colors.red,
                                ),
                              ),
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
}

import 'package:flutter/material.dart';
import '../../services/auth_service.dart';
import '../../services/estudiante/evaluaciones_service.dart';
import '../../services/estudiante/prediccion_service.dart';
import '../../utils/logger.dart';
import '../../widgets/student_drawer.dart';

class RendimientoScreen extends StatefulWidget {
  const RendimientoScreen({super.key});

  @override
  State<RendimientoScreen> createState() => _RendimientoScreenState();
}

class _RendimientoScreenState extends State<RendimientoScreen> {
  bool _isLoading = true;
  String? _error;
  Map<String, dynamic>? _prediccion;
  Map<String, dynamic> _datosPrediccion = {};

  @override
  void initState() {
    super.initState();
    _cargarDatos();
  }

  Future<void> _cargarDatos() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      // Obtener usuario actual
      final usuario = await AuthService.getCurrentUser();
      if (usuario == null) {
        setState(() {
          _error = 'No hay sesión activa';
          _isLoading = false;
        });
        return;
      }

      // Usar ID 145 directamente como en el ejemplo
      final estudianteId = "145"; // Para coincidir con el ejemplo

      // 1. Cargar evaluaciones
      final evaluaciones =
          await EvaluacionesService.obtenerEvaluacionesPorEstudiante(
            estudianteId,
          );

      // 2. Preparar datos para predicción
      final datosPrediccion = PrediccionService.prepararDatosPrediccion(
        evaluaciones,
      );

      // 3. Realizar predicción
      final prediccion = await PrediccionService.predecirRendimiento(
        datosPrediccion,
      );

      setState(() {
        _datosPrediccion = datosPrediccion;
        _prediccion = prediccion;
        _isLoading = false;
      });
    } catch (e) {
      AppLogger.e("Error cargando datos de rendimiento: $e");
      setState(() {
        _error = "Error: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Predicción de Rendimiento'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _cargarDatos),
        ],
      ),
      drawer: StudentDrawer(
        currentUser: null,
        currentRoute: '/student/rendimiento',
      ),
      body:
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _error != null
              ? _buildErrorWidget()
              : _buildResultadoWidget(),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 60, color: Colors.red),
          const SizedBox(height: 16),
          Text(
            _error!,
            textAlign: TextAlign.center,
            style: const TextStyle(fontSize: 16),
          ),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _cargarDatos,
            child: const Text('Reintentar'),
          ),
        ],
      ),
    );
  }

  Widget _buildResultadoWidget() {
    if (_prediccion == null) {
      return const Center(child: Text('No se pudo realizar la predicción'));
    }

    final notaPredicha = _prediccion!['nota_predicha'] ?? 0.0;
    final estado = _prediccion!['estado'] ?? 'Desconocido';

    Color estadoColor = estado == 'Aprobado' ? Colors.green : Colors.red;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Tarjeta principal con la predicción
          Card(
            elevation: 4,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  const Text(
                    'Predicción de Nota Final',
                    style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 24),
                  CircleAvatar(
                    radius: 60,
                    backgroundColor: _getColorForNota(notaPredicha),
                    child: Text(
                      notaPredicha.toStringAsFixed(1),
                      style: const TextStyle(
                        fontSize: 28,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 8,
                    ),
                    decoration: BoxDecoration(
                      color: estadoColor.withAlpha(51), // 0.2 * 255 = 51
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Text(
                      estado,
                      style: TextStyle(
                        color: estadoColor,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Basado en tus calificaciones actuales y asistencia',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                  ),
                ],
              ),
            ),
          ),

          const SizedBox(height: 24),

          // Sección de datos usados para la predicción
          const Text(
            'Datos utilizados para la predicción',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          _buildDatosPrediccionList(),
        ],
      ),
    );
  }

  Widget _buildDatosPrediccionList() {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDatoSection('Parciales', [
              {'nombre': 'Parcial 1', 'valor': _datosPrediccion['parcial1']},
              {'nombre': 'Parcial 2', 'valor': _datosPrediccion['parcial2']},
              {'nombre': 'Parcial 3', 'valor': _datosPrediccion['parcial3']},
            ]),
            const Divider(),
            _buildDatoSection('Prácticos', [
              {'nombre': 'Práctico 1', 'valor': _datosPrediccion['practico1']},
              {'nombre': 'Práctico 2', 'valor': _datosPrediccion['practico2']},
              {'nombre': 'Práctico 3', 'valor': _datosPrediccion['practico3']},
              {'nombre': 'Práctico 4', 'valor': _datosPrediccion['practico4']},
              {'nombre': 'Práctico 5', 'valor': _datosPrediccion['practico5']},
              {'nombre': 'Práctico 6', 'valor': _datosPrediccion['practico6']},
            ]),
            const Divider(),
            _buildDatoSection('Participaciones', [
              {
                'nombre': 'Participación 1',
                'valor': _datosPrediccion['participacion1'],
              },
              {
                'nombre': 'Participación 2',
                'valor': _datosPrediccion['participacion2'],
              },
              {
                'nombre': 'Participación 3',
                'valor': _datosPrediccion['participacion3'],
              },
              {
                'nombre': 'Participación 4',
                'valor': _datosPrediccion['participacion4'],
              },
            ]),
            const Divider(),
            _buildDatoSection('Asistencia', [
              {
                'nombre': 'Porcentaje',
                'valor': _datosPrediccion['asistencias'],
              },
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildDatoSection(String titulo, List<Map<String, dynamic>> datos) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          titulo,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        const SizedBox(height: 8),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children:
              datos.map((dato) {
                final valor = (dato['valor'] as num?)?.toDouble() ?? 0.0;
                return Chip(
                  backgroundColor: _getColorForNota(valor).withAlpha(51),
                  label: Text(
                    '${dato['nombre']}: ${valor.toStringAsFixed(1)}',
                    style: TextStyle(
                      color: _getColorForNota(valor),
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                );
              }).toList(),
        ),
      ],
    );
  }

  Color _getColorForNota(double nota) {
    if (nota >= 90) {
      return Colors.green[700]!;
    } else if (nota >= 80) {
      return Colors.lightGreen;
    } else if (nota >= 70) {
      return Colors.amber[700]!;
    } else if (nota >= 51) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
}

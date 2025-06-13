import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/api_config.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:aplicacion_movil/widgets/loading_overlay.dart';
import 'package:aplicacion_movil/config/theme_config.dart';

class AlertasRendimientoScreen extends StatefulWidget {
  const AlertasRendimientoScreen({Key? key}) : super(key: key);

  @override
  // ignore: library_private_types_in_public_api
  _AlertasRendimientoScreenState createState() =>
      _AlertasRendimientoScreenState();
}

class _AlertasRendimientoScreenState extends State<AlertasRendimientoScreen> {
  bool _isLoading = true;
  String? _error;
  List<dynamic> _alertas = [];
  Map<String, dynamic>? _resumen;

  @override
  void initState() {
    super.initState();
    _cargarAlertas();
  }

  Future<void> _cargarAlertas() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      final token = await AuthService.getToken();
      final userId = await AuthService.getCurrentUserId();

      if (token == null || userId == null) {
        throw Exception('No hay sesión activa');
      }

      final url = Uri.parse(
        '${ApiConfig.baseUrl}/cursos/estudiantes/$userId/alertas-rendimiento/',
      );

      final response = await http.get(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final datos = jsonDecode(response.body);

        setState(() {
          _alertas = datos['alertas'] ?? [];
          _resumen = datos['resumen'];
          _isLoading = false;
        });

        AppLogger.i('Alertas cargadas: ${_alertas.length}');
      } else {
        throw Exception('Error ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      AppLogger.e('Error al cargar alertas', e);
      setState(() {
        _error = 'No se pudieron cargar las alertas: $e';
        _isLoading = false;
        // Generar algunos datos de ejemplo para mostrar la UI
        _generarDatosEjemplo();
      });
    }
  }

  void _generarDatosEjemplo() {
    _alertas = [
      {
        'id': 1,
        'fecha': DateTime.now().subtract(Duration(days: 2)).toIso8601String(),
        'materia': 'Matemáticas Avanzadas',
        'tipo': 'promedio_bajo',
        'promedio_actual': 45.0,
        'nota_minima': 51.0,
        'diferencia': 6.0,
        'trimestre': 'Primer Trimestre 2024',
        'recomendaciones':
            'Consulta con tu profesor y revisa los temas pendientes.',
      },
      {
        'id': 2,
        'fecha': DateTime.now().subtract(Duration(days: 5)).toIso8601String(),
        'materia': 'Programación II',
        'tipo': 'inasistencias',
        'asistencia_actual': 65.0,
        'asistencia_minima': 80.0,
        'diferencia': 15.0,
        'trimestre': 'Primer Trimestre 2024',
        'recomendaciones':
            'Procura no faltar a clases, estás por debajo del mínimo requerido.',
      },
    ];

    _resumen = {
      'total_materias': 8,
      'materias_riesgo': 2,
      'promedio_general': 72.5,
      'peor_materia': 'Matemáticas Avanzadas',
      'peor_promedio': 45.0,
    };
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Alertas de Rendimiento'),
        backgroundColor: AppTheme.primaryColor,
      ),
      body:
          _isLoading
              ? LoadingOverlay(isLoading: true, child: Container())
              : _error != null
              ? _buildErrorWidget()
              : _buildContent(),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.error_outline, size: 80, color: Colors.red),
            SizedBox(height: 16),
            Text(
              'Error',
              style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              _error ?? 'Se produjo un error desconocido',
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _cargarAlertas,
              child: Text('Reintentar'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent() {
    if (_alertas.isEmpty) {
      return _buildNoAlertasWidget();
    }

    return RefreshIndicator(
      onRefresh: _cargarAlertas,
      child: SingleChildScrollView(
        physics: AlwaysScrollableScrollPhysics(),
        padding: EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (_resumen != null) _buildResumenWidget(),
            SizedBox(height: 24),
            Text(
              'Alertas Recientes',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            ..._alertas.map((alerta) => _buildAlertaCard(alerta)),
          ],
        ),
      ),
    );
  }

  Widget _buildNoAlertasWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle_outline, size: 100, color: Colors.green),
          SizedBox(height: 16),
          Text(
            '¡Excelente!',
            style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
          ),
          SizedBox(height: 8),
          Text(
            'No tienes alertas de rendimiento académico.',
            style: TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
          SizedBox(height: 6),
          Text(
            'Sigue así.',
            style: TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildResumenWidget() {
    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Resumen Académico',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 16),
            _buildResumenItem(
              'Materias en Riesgo:',
              '${_resumen?['materias_riesgo']} de ${_resumen?['total_materias']}',
              icon: Icons.warning,
              color: Colors.orange,
            ),
            _buildResumenItem(
              'Promedio General:',
              '${_resumen?['promedio_general']}',
              icon: Icons.grade,
              color:
                  (_resumen?['promedio_general'] ?? 0) >= 51.0
                      ? Colors.green
                      : Colors.red,
            ),
            _buildResumenItem(
              'Materia más baja:',
              '${_resumen?['peor_materia']} (${_resumen?['peor_promedio']})',
              icon: Icons.trending_down,
              color: Colors.red,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResumenItem(
    String label,
    String value, {
    required IconData icon,
    required Color color,
  }) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Row(
        children: [
          Icon(icon, color: color, size: 22),
          SizedBox(width: 8),
          Expanded(child: Text(label, style: TextStyle(fontSize: 16))),
          Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertaCard(Map<String, dynamic> alerta) {
    final bool esPromedioBajo = alerta['tipo'] == 'promedio_bajo';
    final String titulo =
        esPromedioBajo
            ? 'Promedio bajo en ${alerta['materia']}'
            : 'Inasistencias en ${alerta['materia']}';
    final IconData icon = esPromedioBajo ? Icons.grade : Icons.calendar_today;
    final Color color = Colors.red.shade700;

    // Formatear fecha
    final fecha = DateTime.parse(alerta['fecha']);
    final fechaFormateada = '${fecha.day}/${fecha.month}/${fecha.year}';

    return Card(
      margin: EdgeInsets.only(bottom: 16),
      elevation: 3,
      child: Column(
        children: [
          Container(
            padding: EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.only(
                topLeft: Radius.circular(4),
                topRight: Radius.circular(4),
              ),
            ),
            child: Row(
              children: [
                Icon(icon, color: Colors.white),
                SizedBox(width: 12),
                Expanded(
                  child: Text(
                    titulo,
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
                Text(fechaFormateada, style: TextStyle(color: Colors.white70)),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (esPromedioBajo) ...[
                  _buildAlertaPromedioInfo(alerta),
                ] else ...[
                  _buildAlertaAsistenciaInfo(alerta),
                ],
                SizedBox(height: 12),
                Text(
                  'Trimestre: ${alerta['trimestre']}',
                  style: TextStyle(
                    fontStyle: FontStyle.italic,
                    color: Colors.grey[600],
                  ),
                ),
                SizedBox(height: 12),
                Text(
                  '💡 Recomendación:',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
                SizedBox(height: 4),
                Text(alerta['recomendaciones'] ?? ''),
                SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    ElevatedButton(
                      onPressed: () {
                        // Navegar al detalle de la materia
                        Navigator.of(context).pushNamed(
                          '/student/materia/detalle',
                          arguments: {
                            'materia_id': alerta['materia_id'],
                            'materia_nombre': alerta['materia'],
                          },
                        );
                      },
                      style: ElevatedButton.styleFrom(backgroundColor: color),
                      child: Text('Ver Materia'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertaPromedioInfo(Map<String, dynamic> alerta) {
    return Column(
      children: [
        _buildInfoRow(
          'Promedio actual:',
          '${alerta['promedio_actual']}',
          alerta['promedio_actual'] >= 51.0 ? Colors.green : Colors.red,
        ),
        _buildInfoRow(
          'Nota mínima:',
          '${alerta['nota_minima']}',
          Colors.orange,
        ),
        _buildInfoRow(
          'Necesitas subir:',
          '${alerta['diferencia']} pts',
          Colors.red,
        ),
      ],
    );
  }

  Widget _buildAlertaAsistenciaInfo(Map<String, dynamic> alerta) {
    return Column(
      children: [
        _buildInfoRow(
          'Asistencia actual:',
          '${alerta['asistencia_actual']}%',
          alerta['asistencia_actual'] >= 80.0 ? Colors.green : Colors.red,
        ),
        _buildInfoRow(
          'Mínimo requerido:',
          '${alerta['asistencia_minima']}%',
          Colors.orange,
        ),
        _buildInfoRow('Diferencia:', '${alerta['diferencia']}%', Colors.red),
      ],
    );
  }

  Widget _buildInfoRow(String label, String value, Color valueColor) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 15)),
          Text(
            value,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: valueColor,
              fontSize: 15,
            ),
          ),
        ],
      ),
    );
  }
}

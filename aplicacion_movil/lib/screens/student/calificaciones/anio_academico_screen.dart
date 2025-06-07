import 'package:flutter/material.dart';
import 'package:aplicacion_movil/services/estudiante/trimestre_service.dart';

class AnioAcademicoScreen extends StatefulWidget {
  final String titulo;
  final String nextRoute;

  const AnioAcademicoScreen({
    super.key, // Uso de super parameter
    required this.titulo,
    required this.nextRoute,
  });

  @override
  State<AnioAcademicoScreen> createState() => _AnioAcademicoScreenState(); // Corregido
}

class _AnioAcademicoScreenState extends State<AnioAcademicoScreen> {
  final TrimestreService _trimestreService = TrimestreService();
  bool _isLoading = true;
  List<int> _aniosAcademicos = [];
  Map<int, List<dynamic>> _trimestresAgrupados = {};
  String? _error;

  @override
  void initState() {
    super.initState();
    _cargarAniosAcademicos();
  }

  Future<void> _cargarAniosAcademicos() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Usar el nuevo servicio de trimestres
      final aniosConTrimestres =
          await _trimestreService.obtenerAniosAcademicosTrimestres();

      setState(() {
        _aniosAcademicos = aniosConTrimestres.keys.toList();
        _trimestresAgrupados = aniosConTrimestres;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _error = "Error al cargar años académicos: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(widget.titulo), elevation: 0),
      body:
          _isLoading
              ? _loadingWidget() // Widget de carga simple personalizado
              : _error != null
              ? Center(
                child: Text(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              )
              : _aniosAcademicos.isEmpty
              ? const Center(
                child: Text(
                  'No hay años académicos disponibles',
                  style: TextStyle(fontSize: 16),
                ),
              )
              : ListView.builder(
                padding: const EdgeInsets.all(16.0),
                itemCount: _aniosAcademicos.length,
                itemBuilder: (context, index) {
                  return _buildAnioCard(_aniosAcademicos[index]);
                },
              ),
    );
  }

  Widget _buildAnioCard(int anio) {
    // Obtener los trimestres para este año
    final trimestresPorAnio = _trimestresAgrupados[anio] ?? [];

    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            widget
                .nextRoute, // Usar la ruta de navegación pasada como parámetro
            arguments: {'anio': anio, 'trimestres': trimestresPorAnio},
          );
        },
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              Icon(
                Icons.calendar_today,
                size: 32,
                color: Theme.of(context).primaryColor,
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Año Académico $anio',
                      style: const TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${trimestresPorAnio.length} trimestres disponibles',
                      style: TextStyle(color: Colors.grey[600], fontSize: 14),
                    ),
                  ],
                ),
              ),
              Icon(Icons.arrow_forward_ios, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }

  Widget _loadingWidget() {
    return const Center(child: CircularProgressIndicator());
  }
}

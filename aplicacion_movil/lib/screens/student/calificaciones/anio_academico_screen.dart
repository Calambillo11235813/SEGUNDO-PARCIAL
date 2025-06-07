import 'package:flutter/material.dart';
import 'package:aplicacion_movil/services/estudiante/trimestre_service.dart';
import 'package:aplicacion_movil/services/auth_service.dart';

class AnioAcademicoScreen extends StatefulWidget {
  final String titulo;
  final String nextRoute;

  const AnioAcademicoScreen({
    super.key,
    required this.titulo,
    required this.nextRoute,
  });

  @override
  State<AnioAcademicoScreen> createState() => _AnioAcademicoScreenState();
}

class _AnioAcademicoScreenState extends State<AnioAcademicoScreen> {
  final TrimestreService _trimestreService = TrimestreService();
  bool _isLoading = true;
  List<dynamic> _aniosTrimestres = [];
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

      // Obtener el ID del estudiante actual desde AuthService
      final estudianteId = await AuthService.getCurrentUserId();

      if (estudianteId == null) {
        setState(() {
          _error = "No se pudo obtener el ID del estudiante";
          _isLoading = false;
        });
        return;
      }

      // Usar el nuevo servicio para obtener trimestres del estudiante específico
      final aniosTrimestres = await _trimestreService
          .obtenerTrimestresEstudiante(estudianteId);

      setState(() {
        _aniosTrimestres = aniosTrimestres;
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
              ? _loadingWidget()
              : _error != null
              ? Center(
                child: Text(
                  _error!,
                  style: const TextStyle(color: Colors.red),
                  textAlign: TextAlign.center,
                ),
              )
              : _aniosTrimestres.isEmpty
              ? const Center(
                child: Text(
                  'No hay años académicos disponibles',
                  style: TextStyle(fontSize: 16),
                ),
              )
              : ListView.builder(
                padding: const EdgeInsets.all(16.0),
                itemCount: _aniosTrimestres.length,
                itemBuilder: (context, index) {
                  return _buildAnioCard(_aniosTrimestres[index]);
                },
              ),
    );
  }

  Widget _buildAnioCard(Map<String, dynamic> anioData) {
    final int anio = anioData['año'];
    final List<dynamic> trimestres = anioData['trimestres'] ?? [];

    return Card(
      elevation: 3,
      margin: const EdgeInsets.only(bottom: 16),
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            widget.nextRoute,
            arguments: {'anio': anio, 'trimestres': trimestres},
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
                      '${trimestres.length} trimestres disponibles',
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

import 'package:flutter/material.dart';
import 'package:aplicacion_movil/services/tutor/filtros_service.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class AnioAcademicoScreen extends StatefulWidget {
  const AnioAcademicoScreen({super.key});

  @override
  State<AnioAcademicoScreen> createState() => _AnioAcademicoScreenState();
}

class _AnioAcademicoScreenState extends State<AnioAcademicoScreen> {
  bool _isLoading = true;
  List<String> _aniosAcademicos = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAniosAcademicos();
  }

  Future<void> _loadAniosAcademicos() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Intentar cargar los años académicos del servidor
      try {
        final anios = await FiltrosTutorService.obtenerAniosAcademicos();
        setState(() {
          _aniosAcademicos = anios;
          _isLoading = false;
        });
      } catch (e) {
        // Si falla, usar datos estáticos
        AppLogger.w(
          "Error obteniendo años académicos: $e. Usando datos predefinidos.",
        );
        setState(() {
          _aniosAcademicos = ['2025', '2024', '2023', '2022'];
          _isLoading = false;
        });
      }
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
      appBar: AppBar(title: const Text('Años Académicos'), elevation: 0),
      body:
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
                      onPressed: _loadAniosAcademicos,
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              )
              : _aniosAcademicos.isEmpty
              ? const Center(child: Text('No hay años académicos disponibles'))
              : RefreshIndicator(
                onRefresh: _loadAniosAcademicos,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: GridView.builder(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                          crossAxisCount: 2,
                          crossAxisSpacing: 16.0,
                          mainAxisSpacing: 16.0,
                          childAspectRatio: 1.5,
                        ),
                    itemCount: _aniosAcademicos.length,
                    itemBuilder: (context, index) {
                      final anio = _aniosAcademicos[index];
                      return _buildAnioCard(anio);
                    },
                  ),
                ),
              ),
    );
  }

  Widget _buildAnioCard(String anio) {
    final esAnioActual = anio == DateTime.now().year.toString();

    return Card(
      elevation: 3,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: esAnioActual ? AppTheme.primaryColor : Colors.transparent,
          width: esAnioActual ? 2 : 0,
        ),
      ),
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/tutor/estudiantes-anio',
            arguments: {'anio': anio},
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                Icons.calendar_today,
                size: 36,
                color: esAnioActual ? AppTheme.primaryColor : Colors.grey,
              ),
              const SizedBox(height: 8),
              Text(
                'Año $anio',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: esAnioActual ? AppTheme.primaryColor : null,
                ),
              ),
              if (esAnioActual)
                const Text(
                  'Actual',
                  style: TextStyle(
                    color: AppTheme.primaryColor,
                    fontWeight: FontWeight.w500,
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

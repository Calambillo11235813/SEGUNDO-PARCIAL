import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/tutor/filtros_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class EstudianteDetalleScreen extends StatefulWidget {
  final Map<String, dynamic> estudiante;

  const EstudianteDetalleScreen({super.key, required this.estudiante});

  @override
  State<EstudianteDetalleScreen> createState() =>
      _EstudianteDetalleScreenState();
}

class _EstudianteDetalleScreenState extends State<EstudianteDetalleScreen> {
  bool _isLoading = false;
  List<String> _aniosAcademicos = [];
  String? _selectedAnio;
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

      List<String> anios = [];
      try {
        anios = await FiltrosTutorService.obtenerAniosAcademicos();
      } catch (e) {
        // Si falla, usar datos de ejemplo
        AppLogger.w(
          "Error obteniendo años académicos: $e. Usando datos predefinidos.",
        );
        final currentYear = DateTime.now().year;
        anios = [
          (currentYear).toString(),
          (currentYear - 1).toString(),
          (currentYear - 2).toString(),
        ];
      }

      setState(() {
        _aniosAcademicos = anios;
        // Seleccionar el año actual por defecto
        if (anios.isNotEmpty) {
          _selectedAnio = anios[0];
          _loadEstudianteData();
        } else {
          _isLoading = false;
        }
      });
    } catch (e) {
      AppLogger.e("Error cargando años académicos", e);
      setState(() {
        _error = "Error al cargar años académicos: $e";
        _isLoading = false;
      });
    }
  }

  Future<void> _loadEstudianteData() async {
    if (_selectedAnio == null) return;

    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Aquí cargaríamos datos adicionales del estudiante
      // Por ahora usamos la información básica que ya tenemos
      // Simulamos una carga para mostrar el indicador de progreso
      await Future.delayed(const Duration(milliseconds: 500));

      setState(() {
        _isLoading = false;
      });
    } catch (e) {
      AppLogger.e("Error cargando datos del estudiante", e);
      setState(() {
        _error = "Error al cargar datos del estudiante: $e";
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Detalle de ${widget.estudiante['nombre']}'),
        elevation: 0,
      ),
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
                      onPressed: _loadEstudianteData,
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              )
              : SingleChildScrollView(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    // Encabezado con información del estudiante
                    _buildHeaderSection(),

                    // Selector de año académico
                    _buildYearSelector(),

                    // Tarjetas con opciones
                    _buildOptionsSection(),

                    // Información adicional del estudiante
                    _buildAdditionalInfo(),
                  ],
                ),
              ),
    );
  }

  Widget _buildHeaderSection() {
    return Container(
      color: AppTheme.primaryColor,
      padding: const EdgeInsets.all(20),
      child: Column(
        children: [
          CircleAvatar(
            radius: 50,
            backgroundColor: Colors.white,
            child: Text(
              '${widget.estudiante['nombre'][0]}${widget.estudiante['apellido'][0]}',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: AppTheme.primaryColor,
              ),
            ),
          ),
          const SizedBox(height: 16),
          Text(
            '${widget.estudiante['nombre']} ${widget.estudiante['apellido']}',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 8),
          Text(
            'Código: ${widget.estudiante['codigo']}',
            style: const TextStyle(color: Colors.white, fontSize: 16),
          ),
          const SizedBox(height: 4),
          Text(
            widget.estudiante['curso']?['nombre'] ?? 'Sin curso asignado',
            style: const TextStyle(
              color: Colors.white,
              fontSize: 16,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildYearSelector() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Año Académico',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 8),
          _aniosAcademicos.isEmpty
              ? const Text('No hay años académicos disponibles')
              : DropdownButtonFormField<String>(
                value: _selectedAnio,
                decoration: InputDecoration(
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
                ),
                items:
                    _aniosAcademicos.map((String anio) {
                      return DropdownMenuItem<String>(
                        value: anio,
                        child: Text(anio),
                      );
                    }).toList(),
                onChanged: (String? value) {
                  if (value != null && value != _selectedAnio) {
                    setState(() {
                      _selectedAnio = value;
                      _loadEstudianteData();
                    });
                  }
                },
              ),
        ],
      ),
    );
  }

  Widget _buildOptionsSection() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Opciones',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: _buildOptionCard(
                  title: 'Calificaciones',
                  icon: Icons.assessment,
                  color: AppTheme.calificacionesColor,
                  onTap: () {
                    if (_selectedAnio != null) {
                      Navigator.pushNamed(
                        context,
                        '/tutor/calificaciones-estudiante',
                        arguments: {
                          'estudiante': widget.estudiante,
                          'anio': _selectedAnio,
                        },
                      );
                    }
                  },
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildOptionCard(
                  title: 'Asistencias',
                  icon: Icons.calendar_today,
                  color: AppTheme.asistenciaColor,
                  onTap: () {
                    // Navegar a la pantalla de asistencias
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildOptionCard({
    required String title,
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 40, color: color),
              const SizedBox(height: 12),
              Text(
                title,
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAdditionalInfo() {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Información Adicional',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 16),
          Card(
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                children: [
                  _buildInfoRow(
                    'Email',
                    widget.estudiante['email'] ?? 'No registrado',
                  ),
                  const Divider(),
                  _buildInfoRow(
                    'Teléfono',
                    widget.estudiante['telefono'] ?? 'No registrado',
                  ),
                  const Divider(),
                  _buildInfoRow(
                    'Dirección',
                    widget.estudiante['direccion'] ?? 'No registrada',
                  ),
                  const Divider(),
                  _buildInfoRow(
                    'Fecha de Nacimiento',
                    widget.estudiante['fecha_nacimiento'] ?? 'No registrada',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          SizedBox(
            width: 120,
            child: Text(
              label,
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}

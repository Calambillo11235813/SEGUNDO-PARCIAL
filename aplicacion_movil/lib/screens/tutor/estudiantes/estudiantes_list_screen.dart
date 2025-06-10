import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/tutor/tutor_service.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class EstudiantesListScreen extends StatefulWidget {
  const EstudiantesListScreen({super.key}); // Corregido: usando super.key

  @override
  State<EstudiantesListScreen> createState() => _EstudiantesListScreenState();
}

class _EstudiantesListScreenState extends State<EstudiantesListScreen> {
  bool _isLoading = true;
  List<dynamic> _estudiantes = [];
  String? _error;
  final TextEditingController _searchController =
      TextEditingController(); // Corregido: añadiendo final
  List<dynamic> _estudiantesFiltrados = [];

  @override
  void initState() {
    super.initState();
    _loadEstudiantes();
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  Future<void> _loadEstudiantes() async {
    try {
      setState(() {
        _isLoading = true;
        _error = null;
      });

      // Obtener ID del tutor
      final tutorId = await AuthService.getCurrentUserId();
      if (tutorId == null) {
        throw Exception('No se pudo obtener el ID del tutor');
      }

      // Obtener la lista de estudiantes
      // Corregido: pasando tutorId directamente como String
      final result = await TutorService.obtenerEstudiantesTutor(
        tutorId, // No usar int.parse para mantener el tipo String
      );

      final estudiantes = result['estudiantes'] as List<dynamic>;

      setState(() {
        _estudiantes = estudiantes;
        _estudiantesFiltrados = estudiantes;
        _isLoading = false;
      });
    } catch (e, stackTrace) {
      AppLogger.e("Error cargando estudiantes del tutor", e, stackTrace);
      setState(() {
        _error = "Error al cargar estudiantes: $e";
        _isLoading = false;
      });
    }
  }

  void _filterEstudiantes(String query) {
    if (query.isEmpty) {
      setState(() {
        _estudiantesFiltrados = _estudiantes;
      });
      return;
    }

    final lowercaseQuery = query.toLowerCase();
    setState(() {
      _estudiantesFiltrados =
          _estudiantes.where((estudiante) {
            final nombre = estudiante['nombre'].toString().toLowerCase();
            final apellido = estudiante['apellido'].toString().toLowerCase();
            final codigo = estudiante['codigo'].toString().toLowerCase();
            return nombre.contains(lowercaseQuery) ||
                apellido.contains(lowercaseQuery) ||
                codigo.contains(lowercaseQuery);
          }).toList();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis Estudiantes'), elevation: 0),
      body: Column(
        children: [
          // Barra de búsqueda
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Buscar estudiante...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(vertical: 12.0),
              ),
              onChanged: _filterEstudiantes,
            ),
          ),

          // Lista de estudiantes o mensajes
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
                            onPressed: _loadEstudiantes,
                            child: const Text('Reintentar'),
                          ),
                        ],
                      ),
                    )
                    : _estudiantesFiltrados.isEmpty
                    ? Center(
                      child:
                          _estudiantes.isEmpty
                              ? const Text('No tienes estudiantes asignados')
                              : const Text(
                                'No se encontraron estudiantes con esa búsqueda',
                              ),
                    )
                    : RefreshIndicator(
                      onRefresh: _loadEstudiantes,
                      child: ListView.builder(
                        padding: const EdgeInsets.symmetric(horizontal: 16.0),
                        itemCount: _estudiantesFiltrados.length,
                        itemBuilder: (context, index) {
                          final estudiante = _estudiantesFiltrados[index];
                          return _buildEstudianteCard(estudiante);
                        },
                      ),
                    ),
          ),
        ],
      ),
    );
  }

  Widget _buildEstudianteCard(Map<String, dynamic> estudiante) {
    final curso = estudiante['curso'];
    final cursoNombre = curso != null ? curso['nombre'] : 'Sin curso asignado';

    return Card(
      margin: const EdgeInsets.only(bottom: 12.0),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/tutor/estudiante-detalle',
            arguments: {'estudiante': estudiante},
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              // Avatar circular
              CircleAvatar(
                radius: 24,
                backgroundColor: AppTheme.primaryColor,
                child: Text(
                  '${estudiante['nombre'][0]}${estudiante['apellido'][0]}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
              const SizedBox(width: 16),
              // Información del estudiante
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '${estudiante['nombre']} ${estudiante['apellido']}',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Código: ${estudiante['codigo']}',
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                    Text(
                      cursoNombre,
                      style: TextStyle(color: Colors.grey[600]),
                    ),
                  ],
                ),
              ),
              // Icono para acceder a detalles
              const Icon(Icons.chevron_right),
            ],
          ),
        ),
      ),
    );
  }
}

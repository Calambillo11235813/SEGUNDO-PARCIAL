import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';
import 'package:aplicacion_movil/services/tutor/tutor_service.dart';
import 'package:aplicacion_movil/services/auth_service.dart';
import 'package:aplicacion_movil/utils/logger.dart';

class EstudiantesAnioScreen extends StatefulWidget {
  final String anioAcademico;

  const EstudiantesAnioScreen({super.key, required this.anioAcademico});

  @override
  State<EstudiantesAnioScreen> createState() => _EstudiantesAnioScreenState();
}

class _EstudiantesAnioScreenState extends State<EstudiantesAnioScreen> {
  bool _isLoading = true;
  List<dynamic> _estudiantes = [];
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadEstudiantes();
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

  @override
  Widget build(BuildContext context) {
    // Eliminada la variable no utilizada primaryColor

    return Scaffold(
      appBar: AppBar(
        title: Text('Estudiantes - Año ${widget.anioAcademico}'),
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
                      onPressed: _loadEstudiantes,
                      child: const Text('Reintentar'),
                    ),
                  ],
                ),
              )
              : _estudiantes.isEmpty
              ? const Center(child: Text('No tienes estudiantes asignados'))
              : RefreshIndicator(
                onRefresh: _loadEstudiantes,
                child: ListView.builder(
                  padding: const EdgeInsets.all(16.0),
                  itemCount: _estudiantes.length,
                  itemBuilder: (context, index) {
                    final estudiante = _estudiantes[index];
                    return _buildEstudianteCard(estudiante);
                  },
                ),
              ),
    );
  }

  Widget _buildEstudianteCard(Map<String, dynamic> estudiante) {
    final curso = estudiante['curso'];
    final cursoNombre = curso != null ? curso['nombre'] : 'Sin curso asignado';
    final Color primaryColor =
        AppTheme.primaryColor; // Variable local usada en el widget

    return Card(
      margin: const EdgeInsets.only(bottom: 16.0),
      elevation: 3,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () {
          Navigator.pushNamed(
            context,
            '/tutor/calificaciones-estudiante',
            arguments: {'estudiante': estudiante, 'anio': widget.anioAcademico},
          );
        },
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Row(
            children: [
              // Avatar del estudiante
              CircleAvatar(
                radius: 30,
                backgroundColor: primaryColor, // Aquí se usa la variable local
                child: Text(
                  '${estudiante['nombre'][0]}${estudiante['apellido'][0]}',
                  style: const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                    fontSize: 18,
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
                        fontSize: 18,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'Código: ${estudiante['codigo']}',
                      style: TextStyle(color: Colors.grey[600], fontSize: 15),
                    ),
                    Text(
                      cursoNombre,
                      style: TextStyle(
                        color: Colors.grey[700],
                        fontWeight: FontWeight.w500,
                        fontSize: 15,
                      ),
                    ),
                  ],
                ),
              ),
              // Flecha de navegación
              Container(
                width: 40,
                height: 40,
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Icon(
                  Icons.arrow_forward_ios,
                  color: primaryColor, // Aquí se usa la variable local
                  size: 18,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

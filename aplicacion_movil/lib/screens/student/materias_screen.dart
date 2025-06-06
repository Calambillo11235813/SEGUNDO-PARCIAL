import 'package:flutter/material.dart';
import '../../models/usuario.dart';
import '../../services/auth_service.dart';
import '../../services/estudiante/materias_service.dart';
import '../../widgets/student_drawer.dart';

class MateriasScreen extends StatefulWidget {
  const MateriasScreen({super.key});

  @override
  State<MateriasScreen> createState() => _MateriasScreenState();
}

class _MateriasScreenState extends State<MateriasScreen> {
  bool isLoading = true;
  Map<String, dynamic>? cursoData;
  String? errorMessage;
  Usuario? currentUser;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Obtener usuario actual
      final user = await AuthService.getCurrentUser();

      if (user == null) {
        setState(() {
          isLoading = false;
          errorMessage = 'No se pudo obtener la información del usuario';
        });
        return;
      }

      setState(() {
        currentUser = user;
      });

      // Cargar materias
      final data = await MateriasService.obtenerMateriasPorEstudiante(
        user.id.toString(),
      );

      setState(() {
        cursoData = data;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = 'Error al cargar las materias: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis Materias')),
      drawer:
          currentUser != null
              ? StudentDrawer(
                currentUser: currentUser,
                currentRoute: '/student/materias',
              )
              : null,
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : errorMessage != null
              ? Center(child: Text(errorMessage!))
              : _buildMateriasList(),
    );
  }

  Widget _buildMateriasList() {
    if (cursoData == null) {
      return const Center(child: Text('No hay información disponible'));
    }

    final materias = cursoData!['curso']['materias'] as List<dynamic>;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Información del curso
        Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'Curso: ${cursoData!['curso']['nombre']}',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              if (cursoData!['curso']['nivel'] != null) ...[
                const SizedBox(height: 4),
                Text(
                  'Nivel: ${cursoData!['curso']['nivel']['nombre']}',
                  style: const TextStyle(fontSize: 16),
                ),
              ],
              const SizedBox(height: 16),
              Text(
                'Materias (${materias.length})',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
        ),

        // Lista de materias
        Expanded(
          child: ListView.builder(
            itemCount: materias.length,
            itemBuilder: (context, index) {
              final materia = materias[index];
              return Card(
                margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
                child: ListTile(
                  leading: CircleAvatar(
                    backgroundColor: Colors.blueAccent,
                    child: Text('${index + 1}'),
                  ),
                  title: Text(materia['nombre']),
                  subtitle:
                      materia['profesor'] != null
                          ? Text(
                            'Prof. ${materia['profesor']['nombre']} ${materia['profesor']['apellido']}',
                          )
                          : const Text('Sin profesor asignado'),
                  trailing: const Icon(Icons.arrow_forward_ios, size: 16),
                  onTap: () {
                    Navigator.pushNamed(
                      context,
                      '/student/materia/detalle',
                      arguments: {
                        'materia': materia,
                        'curso': cursoData!['curso'],
                      },
                    );
                  },
                ),
              );
            },
          ),
        ),
      ],
    );
  }
}

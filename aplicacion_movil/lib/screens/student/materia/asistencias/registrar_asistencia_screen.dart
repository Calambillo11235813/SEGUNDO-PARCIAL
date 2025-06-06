import 'package:flutter/material.dart';
import '../../../../services/auth_service.dart';
import '../../../../services/estudiante/asistencias_service.dart';
import '../../../../widgets/loading_overlay.dart';

class RegistrarAsistenciaScreen extends StatefulWidget {
  const RegistrarAsistenciaScreen({super.key});

  @override
  State<RegistrarAsistenciaScreen> createState() =>
      _RegistrarAsistenciaScreenState();
}

class _RegistrarAsistenciaScreenState extends State<RegistrarAsistenciaScreen> {
  bool isLoading = false;
  bool asistenciaRegistrada = false;
  String? error;

  @override
  Widget build(BuildContext context) {
    final arguments =
        ModalRoute.of(context)?.settings.arguments as Map<String, dynamic>?;

    if (arguments == null) {
      return const Scaffold(
        body: Center(
          child: Text('Error: No se encontraron datos de la materia'),
        ),
      );
    }

    final materia = arguments['materia'] as Map<String, dynamic>;

    return LoadingOverlay(
      isLoading: isLoading,
      child: Scaffold(
        appBar: AppBar(
          title: Text('Registrar Asistencia - ${materia['nombre']}'),
        ),
        body: Padding(
          padding: const EdgeInsets.all(16.0),
          child:
              asistenciaRegistrada
                  ? _buildExitoRegistro(materia)
                  : _buildFormularioRegistro(materia),
        ),
      ),
    );
  }

  Widget _buildFormularioRegistro(Map<String, dynamic> materia) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.check_circle_outline, size: 80, color: Colors.blue),
          const SizedBox(height: 24),
          Text(
            'Registrar asistencia a ${materia['nombre']}',
            style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          Text(
            'Fecha: ${DateTime.now().day}/${DateTime.now().month}/${DateTime.now().year}',
            style: const TextStyle(fontSize: 18),
          ),
          const SizedBox(height: 32),
          if (error != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: Colors.red[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.red.shade300),
              ),
              child: Row(
                children: [
                  Icon(Icons.error_outline, color: Colors.red[700]),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      error!,
                      style: TextStyle(color: Colors.red[700]),
                    ),
                  ),
                ],
              ),
            ),
          ElevatedButton.icon(
            onPressed: () => _registrarAsistencia(materia),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
              backgroundColor: Colors.green,
              foregroundColor: Colors.white,
            ),
            icon: const Icon(Icons.check),
            label: const Text(
              'Confirmar Asistencia',
              style: TextStyle(fontSize: 18),
            ),
          ),
          const SizedBox(height: 16),
          TextButton.icon(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.arrow_back),
            label: const Text('Volver'),
          ),
        ],
      ),
    );
  }

  Widget _buildExitoRegistro(Map<String, dynamic> materia) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.check_circle, size: 80, color: Colors.green),
          const SizedBox(height: 24),
          const Text(
            '¡Asistencia registrada!',
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Colors.green,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Tu asistencia a ${materia['nombre']} ha sido registrada correctamente para el día de hoy.',
            style: const TextStyle(fontSize: 16),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 32),
          ElevatedButton.icon(
            onPressed: () => Navigator.of(context).pop(),
            icon: const Icon(Icons.check),
            label: const Text('Aceptar'),
          ),
        ],
      ),
    );
  }

  Future<void> _registrarAsistencia(Map<String, dynamic> materia) async {
    setState(() {
      isLoading = true;
      error = null;
    });

    try {
      final usuario = await AuthService.getCurrentUser();
      if (usuario == null) {
        setState(() {
          isLoading = false;
          error = 'No se pudo obtener la información del usuario';
        });
        return;
      }

      final estudianteId = usuario.id.toString();
      final materiaId = materia['id'].toString();

      // Implementación de seguridad (fecha actual del servidor)
      // No permitimos que el usuario especifique una fecha
      await AsistenciasService.registrarAsistencia(
        estudianteId: estudianteId,
        materiaId: materiaId,
        presente: true, // El estudiante confirma que está presente
      );

      setState(() {
        isLoading = false;
        asistenciaRegistrada = true;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        error = e.toString();
      });
    }
  }
}

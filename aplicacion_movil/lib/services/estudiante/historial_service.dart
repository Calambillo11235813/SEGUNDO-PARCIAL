import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../config/api_config.dart'; // Asegúrate de tener la URL base aquí
import '../auth_service.dart';

class HistorialService {
  static Future<Map<String, dynamic>?> obtenerHistorialAcademico(
    int estudianteId,
  ) async {
    final String? token = await AuthService.getToken();
    final url = Uri.parse(
      '${ApiConfig.baseUrl}/cursos/estudiantes/$estudianteId/historial-academico/',
    );

    try {
      final response = await http.get(
        url,
        headers: {
          'Content-Type': 'application/json',
          if (token != null) 'Authorization': 'Bearer $token',
        },
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      } else {
        // Puedes agregar más manejo de errores aquí
        return null;
      }
    } catch (e) {
      // Manejo de error de red o parsing
      return null;
    }
  }
}

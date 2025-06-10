import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/usuario.dart';
import '../utils/logger.dart'; // Añadir esta importación

class AuthService {
  static const storage = FlutterSecureStorage();

  // Método para iniciar sesión
  static Future<Map<String, dynamic>> login(
    String codigo,
    String password,
  ) async {
    final response = await http.post(
      Uri.parse(ApiConfig.loginEndpoint),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'codigo': codigo, 'password': password}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);

      // Guardar tokens en almacenamiento seguro
      await storage.write(key: 'access_token', value: data['tokens']['access']);
      await storage.write(
        key: 'refresh_token',
        value: data['tokens']['refresh'],
      );

      // Guardar información del usuario
      await storage.write(
        key: 'user_id',
        value: data['usuario']['id'].toString(),
      );
      await storage.write(key: 'user_name', value: data['usuario']['nombre']);
      await storage.write(
        key: 'user_lastname',
        value: data['usuario']['apellido'],
      );
      await storage.write(key: 'user_code', value: data['usuario']['codigo']);

      if (data['usuario']['rol'] != null) {
        await storage.write(
          key: 'user_role',
          value: data['usuario']['rol']['nombre'],
        );
      }

      return data;
    } else {
      // Si hay un error, decodificar el mensaje de error
      Map<String, dynamic> errorData;
      try {
        errorData = jsonDecode(response.body);
      } catch (e) {
        throw Exception('Error de conexión. Verifica tu servidor.');
      }
      throw Exception(errorData['error'] ?? 'Error al iniciar sesión');
    }
  }

  // Verificar si hay una sesión activa
  static Future<bool> isLoggedIn() async {
    final token = await storage.read(key: 'access_token');
    return token != null;
  }

  // Obtener información del usuario actual
  static Future<Usuario?> getCurrentUser() async {
    final id = await storage.read(key: 'user_id');
    final nombre = await storage.read(key: 'user_name');
    final apellido = await storage.read(key: 'user_lastname');
    final codigo = await storage.read(key: 'user_code');
    final rolNombre = await storage.read(key: 'user_role');

    if (id == null || nombre == null || apellido == null || codigo == null) {
      return null;
    }

    return Usuario(
      id: int.parse(id),
      nombre: nombre,
      apellido: apellido,
      codigo: codigo,
      rol: rolNombre != null ? {'nombre': rolNombre} : null,
    );
  }

  // Obtener el token de acceso
  static Future<String?> getToken() async {
    return await storage.read(key: 'access_token');
  }

  // Cerrar sesión
  static Future<void> logout() async {
    await storage.deleteAll();
  }

  // Obtener datos del usuario decodificando el token
  static Future<Map<String, dynamic>?> getUserData() async {
    final token = await getToken();
    if (token == null) return null;

    // Decodificar token JWT (si usas JWT)
    try {
      // Esta es una implementación simple - ajusta según tu sistema
      final parts = token.split('.');
      if (parts.length != 3) return null;

      final payload = parts[1];
      final normalized = base64Url.normalize(payload);
      final decoded = utf8.decode(base64Url.decode(normalized));
      final payloadMap = jsonDecode(decoded);

      return {
        'id': payloadMap['sub'] ?? payloadMap['id'],
        'nombre': payloadMap['name'],
        'email': payloadMap['email'],
        // Otros campos que necesites
      };
    } catch (e) {
      AppLogger.e('Error decodificando token:', e);
      return null;
    }
  }

  // Obtener el ID del usuario actual
  static Future<int?> getCurrentUserId() async {
    try {
      AppLogger.d("Intentando leer user_id del almacenamiento");
      final String? userId = await storage.read(key: 'user_id');
      AppLogger.d("Resultado de user_id: $userId");

      // Si userId es null, intenta buscar otras claves posibles
      if (userId == null) {
        final allKeys = await storage.readAll();
        AppLogger.d("Todas las claves disponibles: ${allKeys.keys}");

        // Verifica si hay un key llamado 'user' que podría contener el objeto completo
        final userJson = await storage.read(key: 'user');
        if (userJson != null) {
          try {
            final userData = jsonDecode(userJson);
            AppLogger.d("Datos de usuario encontrados: $userData");
            if (userData['id'] != null) {
              return userData['id'];
            }
          } catch (e) {
            AppLogger.e("Error decodificando datos de usuario", e);
          }
        }
      }

      if (userId != null) {
        return int.parse(userId);
      }

      // Si no se encuentra el ID
      AppLogger.w('No se encontró ID de usuario en el almacenamiento seguro');
      return null;
    } catch (e) {
      AppLogger.e('Error obteniendo ID de usuario', e);
      return null;
    }
  }

  // Añadir este método para verificar el rol del usuario
  static Future<String?> getCurrentUserRole() async {
    try {
      final rolNombre = await storage.read(key: 'user_role');
      return rolNombre;
    } catch (e) {
      AppLogger.e('Error obteniendo rol de usuario', e);
      return null;
    }
  }
}

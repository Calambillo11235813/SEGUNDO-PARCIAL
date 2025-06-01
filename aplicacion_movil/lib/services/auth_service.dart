import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../config/api_config.dart';
import '../models/usuario.dart';

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
}

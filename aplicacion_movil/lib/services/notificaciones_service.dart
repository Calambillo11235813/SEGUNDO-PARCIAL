import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:flutter/material.dart';
import '../utils/logger.dart';
import '../config/api_config.dart';
import './auth_service.dart';

class NotificacionesService {
  static final FirebaseMessaging _firebaseMessaging =
      FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotifications =
      FlutterLocalNotificationsPlugin();
  static bool _initialized = false;

  /// Inicializa el servicio de notificaciones
  static Future<void> inicializar() async {
    if (_initialized) return;

    // Configurar permisos
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    AppLogger.i(
      'Estado de permisos de notificación: ${settings.authorizationStatus}',
    );

    // Configurar notificaciones locales
    final AndroidInitializationSettings androidSettings =
        AndroidInitializationSettings('@mipmap/ic_launcher');
    final DarwinInitializationSettings iosSettings =
        DarwinInitializationSettings(
          requestAlertPermission: true,
          requestBadgePermission: true,
          requestSoundPermission: true,
        );
    final InitializationSettings initSettings = InitializationSettings(
      android: androidSettings,
      iOS: iosSettings,
    );

    await _localNotifications.initialize(
      initSettings,
      onDidReceiveNotificationResponse: _onNotificationTapped,
    );

    // Manejar mensajes en primer plano
    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);

    // Registrar token de dispositivo en el servidor
    await _registrarTokenDispositivo();

    // Escuchar cambios de token
    _firebaseMessaging.onTokenRefresh.listen(_actualizarTokenDispositivo);

    _initialized = true;
  }

  /// Maneja notificaciones recibidas cuando la app está en primer plano
  static void _handleForegroundMessage(RemoteMessage message) {
    AppLogger.i(
      'Notificación recibida en primer plano: ${message.notification?.title}',
    );

    // Mostrar notificación local
    _mostrarNotificacionLocal(
      id: message.hashCode,
      title: message.notification?.title ?? 'Alerta académica',
      body: message.notification?.body ?? '',
      payload: jsonEncode(message.data),
    );
  }

  /// Muestra una notificación local
  static Future<void> _mostrarNotificacionLocal({
    required int id,
    required String title,
    required String body,
    String? payload,
  }) async {
    final AndroidNotificationDetails androidDetails =
        AndroidNotificationDetails(
          'rendimiento_academico_channel',
          'Rendimiento Académico',
          channelDescription: 'Notificaciones sobre rendimiento académico',
          importance: Importance.high,
          priority: Priority.high,
          showWhen: true,
          color: Color(0xFF2196F3),
        );

    final NotificationDetails notificationDetails = NotificationDetails(
      android: androidDetails,
      iOS: DarwinNotificationDetails(),
    );

    await _localNotifications.show(
      id,
      title,
      body,
      notificationDetails,
      payload: payload,
    );
  }

  /// Maneja el evento de toque en una notificación
  static void _onNotificationTapped(NotificationResponse response) {
    AppLogger.i('Notificación tocada: ${response.payload}');

    // Aquí podrías navegar a una pantalla específica según el payload
    // Por ejemplo, abrir la pantalla de detalles de materia
    // Navigator.pushNamed(context, '/student/materia/123');
  }

  /// Registra el token del dispositivo en el servidor
  static Future<void> _registrarTokenDispositivo() async {
    try {
      final token = await _firebaseMessaging.getToken();
      if (token == null) {
        AppLogger.w('No se pudo obtener token FCM');
        return;
      }

      final userId = await AuthService.getCurrentUserId();
      if (userId == null) {
        AppLogger.w('No hay usuario autenticado para registrar token');
        return;
      }

      await _enviarTokenAlServidor(userId.toString(), token);
    } catch (e, stackTrace) {
      AppLogger.e('Error registrando token de dispositivo', e, stackTrace);
    }
  }

  /// Actualiza el token del dispositivo en el servidor cuando cambia
  static Future<void> _actualizarTokenDispositivo(String token) async {
    try {
      final userId = await AuthService.getCurrentUserId();
      if (userId == null) {
        AppLogger.w('No hay usuario autenticado para actualizar token');
        return;
      }

      await _enviarTokenAlServidor(userId.toString(), token);
    } catch (e, stackTrace) {
      AppLogger.e('Error actualizando token de dispositivo', e, stackTrace);
    }
  }

  /// Envía el token FCM al servidor
  static Future<void> _enviarTokenAlServidor(
    String userId,
    String fcmToken,
  ) async {
    try {
      final token = await AuthService.getToken();
      final url = Uri.parse(
        '${ApiConfig.baseUrl}/usuarios/$userId/dispositivos',
      );

      AppLogger.i('Registrando token FCM en servidor: $url');

      final response = await http.post(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'token': fcmToken,
          'plataforma': _obtenerPlataforma(),
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        AppLogger.i('Token FCM registrado exitosamente');
      } else {
        AppLogger.e(
          'Error registrando token FCM: ${response.statusCode} - ${response.body}',
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error enviando token al servidor', e, stackTrace);
    }
  }

  /// Envía una alerta de bajo rendimiento
  static Future<void> enviarAlertaRendimiento({
    required String userId,
    required String titulo,
    required String mensaje,
    required String tipo,
    Map<String, dynamic>? datos,
  }) async {
    try {
      // 1. Intentar enviar a través del servidor (que usará FCM)
      final enviadoPorServidor = await _enviarAlertaPorServidor(
        userId,
        titulo,
        mensaje,
        tipo,
        datos,
      );

      // 2. Si falla el servidor o estamos en desarrollo, mostrar notificación local
      if (!enviadoPorServidor) {
        await _mostrarNotificacionLocal(
          id: DateTime.now().millisecondsSinceEpoch.remainder(100000),
          title: titulo,
          body: mensaje,
          payload: datos != null ? jsonEncode(datos) : null,
        );
      }
    } catch (e, stackTrace) {
      AppLogger.e('Error enviando alerta de rendimiento', e, stackTrace);
      // Intentar mostrar notificación local como fallback
      try {
        await _mostrarNotificacionLocal(
          id: DateTime.now().millisecondsSinceEpoch.remainder(100000),
          title: titulo,
          body: mensaje,
        );
      } catch (e2) {
        AppLogger.e('También falló la notificación local', e2);
      }
    }
  }

  /// Envía una alerta a través del servidor
  static Future<bool> _enviarAlertaPorServidor(
    String userId,
    String titulo,
    String mensaje,
    String tipo,
    Map<String, dynamic>? datos,
  ) async {
    try {
      final token = await AuthService.getToken();
      final url = Uri.parse('${ApiConfig.baseUrl}/notificaciones');

      final response = await http.post(
        url,
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: jsonEncode({
          'usuario_id': userId,
          'titulo': titulo,
          'mensaje': mensaje,
          'tipo': tipo,
          'datos': datos ?? {},
        }),
      );

      return response.statusCode == 200 || response.statusCode == 201;
    } catch (e) {
      AppLogger.e('Error enviando alerta por servidor', e);
      return false;
    }
  }

  /// Determina la plataforma actual para el registro del token
  static String _obtenerPlataforma() {
    // Implementar lógica para detectar plataforma
    // Por ahora retornamos un valor fijo
    return 'android'; // o 'ios'
  }

  /// Muestra una notificación local genérica
  static Future<void> mostrarNotificacion({
    required String titulo,
    required String cuerpo,
    Map<String, dynamic>? payload,
  }) async {
    try {
      // Generar un ID único para la notificación
      final notificationId = DateTime.now().millisecondsSinceEpoch ~/ 1000;

      // Preparar los detalles de la notificación
      final androidDetails = AndroidNotificationDetails(
        'academic_alerts_channel',
        'Alertas Académicas',
        channelDescription: 'Notificaciones sobre rendimiento académico',
        importance: Importance.high,
        priority: Priority.high,
        icon: '@mipmap/ic_launcher',
      );

      final notificationDetails = NotificationDetails(
        android: androidDetails,
        iOS: DarwinNotificationDetails(),
      );

      // Convertir el payload a un formato compatible con las notificaciones locales
      final payloadStr = payload != null ? jsonEncode(payload) : null;

      // Mostrar la notificación
      await _localNotifications.show(
        notificationId,
        titulo,
        cuerpo,
        notificationDetails,
        payload: payloadStr,
      );

      AppLogger.i('Notificación local mostrada: $titulo');
    } catch (e, stackTrace) {
      AppLogger.e('Error al mostrar notificación local', e, stackTrace);
    }
  }
}

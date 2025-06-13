// Este archivo normalmente se generaría automáticamente con flutterfire configure
// Estamos creando uno mínimo para demostración

import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    // En una aplicación real, estos valores provendrían de tu proyecto Firebase
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        return ios;
      default:
        throw UnsupportedError(
          'DefaultFirebaseOptions are not supported for this platform.',
        );
    }
  }

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'tu-api-key-aqui',
    appId: 'tu-app-id-aqui',
    messagingSenderId: 'tu-sender-id-aqui',
    projectId: 'tu-project-id-aqui',
  );

  static const FirebaseOptions ios = FirebaseOptions(
    apiKey: 'tu-api-key-aqui',
    appId: 'tu-app-id-aqui',
    messagingSenderId: 'tu-sender-id-aqui',
    projectId: 'tu-project-id-aqui',
  );
}

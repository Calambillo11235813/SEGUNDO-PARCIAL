import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class UsuariosService {
  private apiUrl = 'http://localhost:8000/api/usuarios';
  
  constructor(private http: HttpClient) { }
  
  // Obtener todos los usuarios
  getUsuarios(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/`);
  }
  
  // Obtener usuarios por rol (filtrado en frontend)
  getUsuariosPorRol(rolNombre: string): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/`).pipe(
      map(usuarios => usuarios.filter(usuario => usuario.rol?.nombre === rolNombre))
    );
  }
  
  // Crear un nuevo usuario (estudiante o profesor)
  crearUsuario(usuario: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/register/`, usuario);
  }
  
  // Obtener un usuario específico
  getUsuario(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/${id}/`);
  }
  
  // Actualizar un usuario
  actualizarUsuario(id: number, usuario: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/usuarios/${id}/update/`, usuario);
  }
  
  // Eliminar un usuario
  eliminarUsuario(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/usuarios/${id}/delete/`);
  }

  /**
   * Cambiar la contraseña de un usuario
   * @param id ID del usuario
   * @param datos Objeto con passwordActual y passwordNuevo
   */
  cambiarPassword(id: number, datos: { passwordActual: string, passwordNuevo: string }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/usuarios/${id}/cambiar-password/`, datos);
  }
}
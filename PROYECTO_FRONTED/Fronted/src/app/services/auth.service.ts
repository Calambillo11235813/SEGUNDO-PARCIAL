import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/usuarios';
  
  constructor(private http: HttpClient) { }

  // Método para iniciar sesión
  login(credenciales: {codigo: string, password: string}): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/auth/login/`, credenciales)
      .pipe(
        tap(response => {
          // Guardar tokens en localStorage
          localStorage.setItem('access_token', response.tokens.access);
          localStorage.setItem('refresh_token', response.tokens.refresh);
          // Asegúrate de guardar el objeto completo del usuario
          localStorage.setItem('currentUser', JSON.stringify(response.usuario));
          localStorage.setItem('token', response.token);
        })
      );
  }

  // Método para registrar un usuario
  register(usuario: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register/`, usuario);
  }

  // Método para cerrar sesión
  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('usuario');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('token');
  }

  // Verificar si el usuario está autenticado
  isAuthenticated(): boolean {
    return localStorage.getItem('access_token') !== null;
  }

  // Obtener el token de acceso
  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  // Obtener los datos del usuario actual
  getCurrentUser(): any {
    const userStr = localStorage.getItem('currentUser');
    return userStr ? JSON.parse(userStr) : null;
  }

  // Verificar si el usuario tiene un rol específico
  hasRole(roleName: string): boolean {
    const usuario = this.getCurrentUser();
    return usuario?.rol?.nombre === roleName;
  }

  // Métodos de conveniencia para roles comunes
  isAdmin(): boolean {
    return this.hasRole('Administrador');
  }

  isTeacher(): boolean {
    return this.hasRole('Profesor');
  }

  isStudent(): boolean {
    return this.hasRole('Estudiante');
  }

  /**
   * Actualiza los datos del usuario en el almacenamiento local
   * @param usuario Datos actualizados del usuario
   */
  updateUserData(usuario: any): void {
    localStorage.setItem('currentUser', JSON.stringify(usuario));
  }
}
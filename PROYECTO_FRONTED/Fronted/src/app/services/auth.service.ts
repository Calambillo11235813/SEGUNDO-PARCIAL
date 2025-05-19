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
    return this.http.post(`${this.apiUrl}/auth/login/`, credenciales)
      .pipe(
        tap((response: any) => {
          // Guardar tokens en localStorage
          localStorage.setItem('access_token', response.tokens.access);
          localStorage.setItem('refresh_token', response.tokens.refresh);
          localStorage.setItem('usuario', JSON.stringify(response.usuario));
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
    const usuario = localStorage.getItem('usuario');
    return usuario ? JSON.parse(usuario) : null;
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UsuarioService {
  private apiUrl = 'http://localhost:8000/api/usuarios'; // Cambia esto por tu URL base del backend

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la cantidad total de estudiantes.
   */
  getCantidadEstudiantes(): Observable<{ total: number }> {
    return this.http.get<{ total: number }>(`${this.apiUrl}/usuarios/estudiantes/`);
  }

  /**
   * Obtiene la cantidad total de profesores.
   */
  getCantidadProfesores(): Observable<{ total: number }> {
    return this.http.get<{ total: number }>(`${this.apiUrl}/usuarios/profesores/`);
  }

}
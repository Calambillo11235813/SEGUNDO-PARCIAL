import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class UsuarioService {
  private apiUrl = 'http://localhost:8000/api/usuarios'; // URL base para usuarios
  private cursosApiUrl = 'http://localhost:8000/api/cursos'; // URL base para cursos

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

  /**
   * Obtiene la cantidad total de cursos.
   */
  getCantidadCursos(): Observable<{ cantidad_cursos: number }> {
    return this.http.get<{ cantidad_cursos: number }>(`${this.cursosApiUrl}/cursos/cantidad/`);
  }
}
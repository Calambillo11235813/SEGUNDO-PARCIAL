import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root',
})
export class UsuarioService {
  private usuariosApiUrl = ApiConfig.ENDPOINTS.USUARIOS;
  private cursosApiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) {}

  /**
   * Obtiene la cantidad total de estudiantes.
   */
  getCantidadEstudiantes(): Observable<{ total: number }> {
    return this.http.get<{ total: number }>(`${this.usuariosApiUrl}/usuarios/estudiantes/`);
  }

  /**
   * Obtiene la cantidad total de profesores.
   */
  getCantidadProfesores(): Observable<{ total: number }> {
    return this.http.get<{ total: number }>(`${this.usuariosApiUrl}/usuarios/profesores/`);
  }

  /**
   * Obtiene la cantidad total de cursos.
   */
  getCantidadCursos(): Observable<{ cantidad_cursos: number }> {
    return this.http.get<{ cantidad_cursos: number }>(`${this.cursosApiUrl}/cursos/cantidad/`);
  }

  /**
   * Obtiene la cantidad total de materias.
   */
  getCantidadMaterias(): Observable<{ cantidad_materias: number }> {
    return this.http.get<{ cantidad_materias: number }>(`${this.cursosApiUrl}/materias/cantidad/`);
  }
}
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class CursosService {
  private apiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  // Obtener todos los cursos con información del nivel
  getCursos(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/cursos/`);
  }

  // Obtener un curso por ID
  getCurso(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cursos/${id}/`);
  }

  // Crear un nuevo curso
  createCurso(cursoData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/cursos/create/`, cursoData);
  }

  // Actualizar un curso existente
  updateCurso(id: number, cursoData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/cursos/${id}/update/`, cursoData);
  }

  // Eliminar un curso
  deleteCurso(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/cursos/${id}/delete/`);
  }

  // Obtener cursos por nivel
  getCursosPorNivel(nivelId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/niveles/${nivelId}/cursos/`);
  }

  /**
   * Asigna un estudiante a un curso
   */
  asignarEstudianteACurso(estudianteId: number, cursoId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/cursos/asignar-estudiante/`, {
      estudiante_id: estudianteId,
      curso_id: cursoId
    });
  }

  /**
   * Obtiene los estudiantes de un curso específico
   */
  getEstudiantesDeCurso(cursoId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cursos/${cursoId}/estudiantes/`);
  }

  /**
   * ✅ NUEVO: Obtiene estudiantes que no tienen curso asignado
   */
  getEstudiantesSinCurso(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/estudiantes/sin-curso/`);
  }

  /**
   * Desasigna un estudiante de su curso
   */
  desasignarEstudianteDeCurso(estudianteId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/estudiantes/${estudianteId}/desasignar-curso/`);
  }
}
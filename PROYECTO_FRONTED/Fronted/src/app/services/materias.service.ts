import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class MateriasService {
  private apiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  // Obtener todas las materias
  getMaterias(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/materias/`);
  }

  // Obtener una materia por ID
  getMateria(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/materias/${id}/`);
  }

  // Crear una nueva materia
  createMateria(materiaData: any): Observable<any> {
    // Ajuste para usar la API correcta según el nuevo backend
    return this.http.post<any>(`${this.apiUrl}/materias/create-por-curso/`, {
      nombre: materiaData.nombre,
      curso_id: materiaData.curso
    });
  }

  // Actualizar una materia existente
  updateMateria(id: number, materiaData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/materias/${id}/update/`, {
      nombre: materiaData.nombre,
      curso: materiaData.curso
    });
  }

  // Eliminar una materia
  deleteMateria(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/materias/${id}/delete/`);
  }

  // Obtener materias por curso
  getMateriasPorCurso(cursoId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/${cursoId}/materias/`);
  }

  // Asignar profesor a materia
  asignarProfesor(materiaId: number, profesorId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/materias/${materiaId}/asignar-profesor/`, {
      profesor_id: profesorId
    });
  }

  // Desasignar profesor de materia
  desasignarProfesor(materiaId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/materias/${materiaId}/desasignar-profesor/`, {});
  }

  // Obtener materias por profesor
  getMateriasPorProfesor(profesorId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/profesores/${profesorId}/materias/`);
  }

  /**
   * Obtiene los datos completos de un curso específico por ID
   */
  getCursoDetalle(cursoId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cursos/${cursoId}/`);
  }

  /**
   * Obtiene los estudiantes de un curso específico
   */
  getEstudiantesDeCurso(cursoId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/cursos/${cursoId}/estudiantes/`);
  }
}
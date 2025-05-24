import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CursosService {
  private apiUrl = 'http://localhost:8000/api/cursos';

  constructor(private http: HttpClient) { }

  // Obtener todos los cursos
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
}
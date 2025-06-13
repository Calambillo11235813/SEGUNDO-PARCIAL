import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class NivelesService {
  private apiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  // Obtener todos los niveles
  getNiveles(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/niveles/`);
  }

  // Obtener un nivel por ID
  getNivel(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/niveles/${id}/`);
  }

  // Crear un nuevo nivel
  createNivel(nivelData: any): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/niveles/create/`, nivelData);
  }

  // Actualizar un nivel existente
  updateNivel(id: number, nivelData: any): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/niveles/${id}/update/`, nivelData);
  }

  // Eliminar un nivel
  deleteNivel(id: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/niveles/${id}/delete/`);
  }
}
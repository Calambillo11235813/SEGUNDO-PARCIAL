import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class AsistenciasService {
  private cursosApiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  /**
   * Obtiene los trimestres disponibles
   */
  getTrimestres(filtros?: { año?: number, activos?: boolean }): Observable<any> {
    let url = `${this.cursosApiUrl}/trimestres/`;
    
    if (filtros) {
      let params = new HttpParams();
      if (filtros.año) params = params.append('año', filtros.año.toString());
      return this.http.get<any>(url, { params });
    }
    
    return this.http.get<any>(url);
  }

  /**
   * Registra asistencias para un trimestre específico
   */
  registrarAsistenciasMasivo(asistenciasData: {
    materia_id: number;
    fecha?: string;
    trimestre_id: number;
    asistencias: Array<{
      estudiante_id: number;
      presente: boolean;
      justificada?: boolean;
    }>;
  }): Observable<any> {
    if (!asistenciasData.trimestre_id) {
      throw new Error('trimestre_id es requerido');
    }
    
    if (!asistenciasData.materia_id) {
      throw new Error('materia_id es requerido');
    }
    
    const url = `${this.cursosApiUrl}/asistencias/registrar-masivo/`;
    
    const dataParaBackend = {
      materia_id: asistenciasData.materia_id,
      trimestre_id: asistenciasData.trimestre_id,
      fecha: asistenciasData.fecha,
      asistencias: asistenciasData.asistencias
    };
    
    console.log('Enviando datos al backend:', dataParaBackend);
    console.log('URL completa:', url);
    
    return this.http.post<any>(url, dataParaBackend).pipe(
      catchError(error => {
        console.error('Error completo:', error);
        console.error('Respuesta del servidor:', error.error);
        throw error;
      })
    );
  }

  /**
   * Registra asistencia individual
   */
  registrarAsistencia(asistenciaData: {
    materia_id: number;
    estudiante_id: number;
    trimestre_id: number;
    fecha?: string;
    presente: boolean;
    justificada?: boolean;
  }): Observable<any> {
    if (!asistenciaData.trimestre_id) {
      throw new Error('trimestre_id es requerido');
    }
    
    const url = `${this.cursosApiUrl}/asistencias/registrar/`;
    return this.http.post<any>(url, asistenciaData);
  }

  /**
   * Obtiene la lista de estudiantes por materia
   */
  getEstudiantesPorMateria(materiaId: number): Observable<any> {
    return this.http.get<any>(`${this.cursosApiUrl}/materias/${materiaId}/estudiantes/`);
  }

  /**
   * Obtiene las asistencias de una materia específica
   */
  getAsistenciasPorMateria(materiaId: number, filtros?: any): Observable<any> {
    let url = `${this.cursosApiUrl}/materias/${materiaId}/asistencias/`;
    
    if (filtros) {
      let params = new HttpParams();
      Object.keys(filtros).forEach(key => {
        if (filtros[key]) {
          params = params.append(key, filtros[key].toString());
        }
      });
      
      return this.http.get<any>(url, { params });
    }
    
    return this.http.get<any>(url);
  }
}
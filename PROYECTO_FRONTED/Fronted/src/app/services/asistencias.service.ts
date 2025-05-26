import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AsistenciasService {
  private apiUrl = 'http://localhost:8000/api/cursos';

  constructor(private http: HttpClient) { }

  /**
   * Registra la asistencia de un estudiante para una materia específica
   */
  registrarAsistencia(asistenciaData: {
    materia_id: number;
    estudiante_id: number;
    fecha?: string;
    presente: boolean;
    justificada?: boolean;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/asistencias/registrar/`, asistenciaData);
  }

  /**
   * Registra asistencias de múltiples estudiantes para una materia
   */
  registrarAsistenciasMasivo(asistenciasData: {
    materia_id: number;
    fecha?: string;
    asistencias: Array<{
      estudiante_id: number;
      presente: boolean;
      justificada?: boolean;
    }>;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/asistencias/registrar-masivo/`, asistenciasData);
  }

  /**
   * Obtiene las asistencias de una materia específica
   */
  getAsistenciasPorMateria(materiaId: number, filtros?: {
    fecha?: string;
    desde?: string;
    hasta?: string;
  }): Observable<any> {
    let url = `${this.apiUrl}/materias/${materiaId}/asistencias/`;
    
    if (filtros) {
      const params = new URLSearchParams();
      if (filtros.fecha) params.append('fecha', filtros.fecha);
      if (filtros.desde) params.append('desde', filtros.desde);
      if (filtros.hasta) params.append('hasta', filtros.hasta);
      
      const queryString = params.toString();
      if (queryString) {
        url += '?' + queryString;
      }
    }
    
    return this.http.get<any>(url);
  }

  /**
   * Obtiene la lista de estudiantes por materia
   */
  getEstudiantesPorMateria(materiaId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/materias/${materiaId}/estudiantes/`);
  }
}
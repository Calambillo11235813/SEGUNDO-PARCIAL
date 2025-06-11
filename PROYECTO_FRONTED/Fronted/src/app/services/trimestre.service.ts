import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class TrimestreService {
  private apiUrl = 'http://localhost:8000/api/cursos'; // URL base similar a otros servicios

  constructor(private http: HttpClient) { }

  /**
   * Obtiene los trimestres con opciones de filtrado
   * @param año - Opcional: Filtrar por año académico
   * @param soloActivos - Opcional: Si es true, solo devuelve trimestres activos
   */
  getTrimestres(año?: number, soloActivos: boolean = false): Observable<any> {
    let params = new HttpParams();
    
    if (año) {
      params = params.append('año', año.toString());
    }
    
    if (soloActivos) {
      params = params.append('activos', 'true');
    }
    
    return this.http.get(`${this.apiUrl}/trimestres/`);
  }

  /**
   * Obtiene los trimestres del año actual
   */
  getTrimestresActuales(): Observable<any> {
    const añoActual = new Date().getFullYear();
    return this.getTrimestres(añoActual, true);
  }

  /**
   * Crea un nuevo trimestre
   */
  crearTrimestre(trimestreData: {
    numero: number;
    nombre: string;
    año_academico: number;
    fecha_inicio: string;
    fecha_fin: string;
    fecha_limite_evaluaciones?: string;
    fecha_limite_calificaciones?: string;
    nota_minima_aprobacion?: number;
    porcentaje_asistencia_minima?: number;
    estado?: string;
    created_by?: number;
  }): Observable<any> {
    return this.http.post(`${this.apiUrl}/trimestres/create/`, trimestreData);
  }

  /**
   * Actualiza un trimestre existente
   */
  actualizarTrimestre(trimestreId: number, trimestreData: {
    nombre?: string;
    fecha_inicio?: string;
    fecha_fin?: string;
    fecha_limite_evaluaciones?: string;
    fecha_limite_calificaciones?: string;
    estado?: string;
    nota_minima_aprobacion?: number;
    porcentaje_asistencia_minima?: number;
  }): Observable<any> {
    return this.http.put(`${this.apiUrl}/trimestres/${trimestreId}/`, trimestreData);
  }

  /**
   * Calcula los promedios de un trimestre para todas las materias y estudiantes
   * @param trimestreId - ID del trimestre para el que se calculan los promedios
   * @param options - Opciones adicionales para filtrar el cálculo
   */
  calcularPromediosTrimestre(trimestreId: number, options?: {
    solo_materia_id?: number;
    solo_estudiantes?: number[];
  }): Observable<any> {
    return this.http.post(`${this.apiUrl}/trimestres/${trimestreId}/calcular-promedios/`, options || {});
  }

  /**
   * Calcula los promedios anuales para todas las materias y estudiantes de un año académico
   * @param añoAcademico - Año académico para el que se calculan los promedios
   */
  calcularPromediosAnuales(añoAcademico: number): Observable<any> {
    return this.http.post(`${this.apiUrl}/años/${añoAcademico}/calcular-promedios-anuales/`, {});
  }

  /**
   * Obtiene un reporte trimestral completo
   * @param trimestreId - ID del trimestre para el que se genera el reporte
   * @param materiaId - Opcional: Filtrar por materia
   * @param cursoId - Opcional: Filtrar por curso
   */
  getReporteTrimestral(trimestreId: number, materiaId?: number, cursoId?: number): Observable<any> {
    let params = new HttpParams();
    
    if (materiaId) {
      params = params.append('materia_id', materiaId.toString());
    }
    
    if (cursoId) {
      params = params.append('curso_id', cursoId.toString());
    }
    
    return this.http.get(`${this.apiUrl}/trimestres/${trimestreId}/reporte/`, { params });
  }

  /**
   * Obtiene un reporte anual comparativo por trimestres
   * @param añoAcademico - Año académico para el que se genera el reporte
   * @param estudianteId - Opcional: Filtrar por estudiante
   * @param cursoId - Opcional: Filtrar por curso
   */
  getReporteAnualComparativo(añoAcademico: number, estudianteId?: number, cursoId?: number): Observable<any> {
    let params = new HttpParams();
    
    if (estudianteId) {
      params = params.append('estudiante_id', estudianteId.toString());
    }
    
    if (cursoId) {
      params = params.append('curso_id', cursoId.toString());
    }
    
    return this.http.get(`${this.apiUrl}/años/${añoAcademico}/reporte-anual-comparativo/`, { params });
  }

  /**
   * Formatea una fecha para el backend (YYYY-MM-DD)
   */
  formatearFechaParaBackend(fecha: Date | string): string {
    if (!fecha) return '';
    
    const fechaObj = typeof fecha === 'string' ? new Date(fecha) : fecha;
    
    const año = fechaObj.getFullYear();
    const mes = String(fechaObj.getMonth() + 1).padStart(2, '0');
    const dia = String(fechaObj.getDate()).padStart(2, '0');
    
    return `${año}-${mes}-${dia}`;
  }

  /**
   * Obtiene el trimestre actual basado en la fecha actual
   */
  obtenerTrimestreActual(): Observable<any> {
    const fechaActual = new Date();
    const añoActual = fechaActual.getFullYear();
    
    return this.getTrimestres(añoActual).pipe(
      map(trimestres => {
        if (!Array.isArray(trimestres) || trimestres.length === 0) {
          return null;
        }
        
        // Buscar el trimestre actual basado en el rango de fechas
        return trimestres.find(trimestre => {
          const fechaInicio = new Date(trimestre.fecha_inicio);
          const fechaFin = new Date(trimestre.fecha_fin);
          return fechaActual >= fechaInicio && fechaActual <= fechaFin;
        }) || null;
      })
    );
  }
}
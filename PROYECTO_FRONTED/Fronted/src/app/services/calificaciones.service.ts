import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable, of, throwError } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class CalificacionesService {
  private apiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  /**
   * Registra la calificación de un estudiante en una evaluación específica
   */
  registrarCalificacion(calificacionData: {
    evaluacion_id: number | null;
    estudiante_id: number;
    tipo_evaluacion: 'entregable' | 'participacion';
    nota: number;
    observaciones?: string;
    retroalimentacion?: string;
    fecha_entrega?: string;
    entrega_tardia?: boolean;
  }): Observable<any> {
    // Validamos que la evaluación no sea null
    if (calificacionData.evaluacion_id === null) {
      return throwError(() => new Error('ID de evaluación no especificado'));
    }
    
    return this.http.post<any>(`${this.apiUrl}/calificaciones/registrar/`, calificacionData);
  }

  /**
   * Registra calificaciones para múltiples estudiantes en una evaluación
   */
  registrarCalificacionesMasivo(calificacionesData: {
    evaluacion_id: number | null;
    tipo_evaluacion: 'entregable' | 'participacion';
    calificaciones: Array<{
      estudiante_id: number;
      nota: number;
      observaciones?: string;
      retroalimentacion?: string;
    }>;
  }): Observable<any> {
    // Validamos que la evaluación no sea null
    if (calificacionesData.evaluacion_id === null) {
      return throwError(() => new Error('ID de evaluación no especificado'));
    }
    
    return this.http.post<any>(`${this.apiUrl}/calificaciones/registrar-masivo/`, calificacionesData);
  }

  /**
   * Obtiene calificaciones por evaluación
   * Ahora acepta evaluacionId que puede ser null
   */
  getCalificacionesPorEvaluacion(evaluacionId: number | null, tipoEvaluacion: 'entregable' | 'participacion'): Observable<any> {
    // Si es null, retornamos un observable con un array vacío
    if (evaluacionId === null) {
      return of({ calificaciones: [] });
    }
    
    return this.http.get<any>(`${this.apiUrl}/evaluaciones/${evaluacionId}/calificaciones/?tipo=${tipoEvaluacion}`);
  }

  /**
   * Obtiene todas las calificaciones de un estudiante específico
   */
  getCalificacionesPorEstudiante(
    estudianteId: number, 
    filtros?: { 
      materia_id?: number; 
      tipo_evaluacion?: string 
    }
  ): Observable<any> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.tipo_evaluacion) params = params.append('tipo_evaluacion', filtros.tipo_evaluacion);
    }
    
    return this.http.get<any>(
      `${this.apiUrl}/estudiantes/${estudianteId}/calificaciones/`,
      { params }
    );
  }

  /**
   * Obtiene un reporte completo de calificaciones para una materia específica
   */
  getReporteCalificacionesMateria(materiaId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/materias/${materiaId}/reporte-calificaciones/`);
  }

  /**
   * Calcula el promedio ponderado de calificaciones
   */
  calcularPromedioPonderado(calificaciones: any[]): number {
    if (!calificaciones || calificaciones.length === 0) return 0;

    let sumaPonderada = 0;
    let sumaPonderaciones = 0;

    calificaciones.forEach(cal => {
      if (cal.nota !== null && cal.evaluacion?.porcentaje_nota_final) {
        sumaPonderada += cal.nota * cal.evaluacion.porcentaje_nota_final;
        sumaPonderaciones += cal.evaluacion.porcentaje_nota_final;
      }
    });

    return sumaPonderaciones > 0 ? Math.round((sumaPonderada / sumaPonderaciones) * 100) / 100 : 0;
  }

  /**
   * Determina si un estudiante está aprobado basado en sus calificaciones
   */
  estaAprobado(promedio: number, notaMinima: number = 51.0): boolean {
    return promedio >= notaMinima;
  }

  /**
   * Genera un color representativo según la calificación
   */
  getColorPorNota(nota: number | null | undefined, notaMinima: number = 51.0): string {
    if (nota === null || nota === undefined) return 'gray';
    
    if (nota < notaMinima) return 'red';
    
    // Escala de color entre amarillo y verde
    const porcentaje = Math.min(100, Math.max(0, ((nota - notaMinima) / (100 - notaMinima)) * 100));
    
    if (porcentaje < 30) return 'orange';
    if (porcentaje < 70) return '#9ACD32'; // YellowGreen
    return 'green';
  }

  /**
   * Convierte una nota numérica a una escala cualitativa
   */
  getEscalaCualitativa(nota: number | null | undefined): string {
    if (nota === null || nota === undefined) return 'Sin calificar';
    
    if (nota < 51) return 'Reprobado';
    if (nota < 70) return 'Regular';
    if (nota < 80) return 'Bueno';
    if (nota < 90) return 'Muy Bueno';
    return 'Excelente';
  }

  /**
   * Verifica si un estudiante tiene todas las evaluaciones calificadas
   */
  tieneTodasLasEvaluacionesCalificadas(evaluaciones: any[], calificacionesEstudiante: any): boolean {
    if (!evaluaciones || !calificacionesEstudiante) return false;
    
    return evaluaciones.every(evaluacion => {
      const idEvaluacion = evaluacion.id.toString();
      return calificacionesEstudiante[idEvaluacion] && 
             calificacionesEstudiante[idEvaluacion].nota !== null;
    });
  }

  /**
   * Formatea la nota para mostrar con 2 decimales
   */
  formatearNota(nota: number | null | undefined): string {
    if (nota === null || nota === undefined) return 'N/A';
    return nota.toFixed(2);
  }

  /**
   * Verifica el progreso de calificación (porcentaje de estudiantes calificados)
   */
  calcularProgresoCalificaciones(estudiantes: any[], evaluacionId: string): number {
    if (!estudiantes || estudiantes.length === 0) return 0;
    
    const calificados = estudiantes.filter(est => 
      est.calificaciones[evaluacionId] && 
      est.calificaciones[evaluacionId].nota !== null
    );
    
    return Math.round((calificados.length / estudiantes.length) * 100);
  }
}
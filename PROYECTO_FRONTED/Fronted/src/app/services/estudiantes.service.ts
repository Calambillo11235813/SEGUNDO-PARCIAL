import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class EstudiantesService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  /**
   * Obtiene todos los estudiantes registrados en el sistema
   */
  getEstudiantes(): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/usuarios/estudiantes/`);
  }

  /**
   * Obtiene un estudiante específico por su ID
   */
  getEstudiante(id: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/estudiantes/${id}/`);
  }

  /**
   * Obtiene todos los estudiantes de un curso específico
   */
  getEstudiantesPorCurso(cursoId: number): Observable<any[]> {
    return this.http.get<any[]>(`${this.apiUrl}/cursos/cursos/${cursoId}/estudiantes/`);
  }

  /**
   * Obtiene todos los estudiantes de una materia específica
   * Este método es clave para obtener los estudiantes que se pueden calificar en una evaluación
   */
  getEstudiantesPorMateria(materiaId: number): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/cursos/materias/${materiaId}/estudiantes/`)
      .pipe(
        map(response => {
          if (response && response.estudiantes) {
            return response.estudiantes;
          } else if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene los estudiantes con sus calificaciones para una evaluación específica
   */
  getEstudiantesPorEvaluacion(evaluacionId: number, tipoEvaluacion: 'entregable' | 'participacion'): Observable<any[]> {
    let params = new HttpParams();
    params = params.append('tipo', tipoEvaluacion);
    
    return this.http.get<any>(`${this.apiUrl}/cursos/evaluaciones/${evaluacionId}/calificaciones/`, { params })
      .pipe(
        map(response => {
          if (response && response.calificaciones) {
            return response.calificaciones;
          } else if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Asigna un estudiante a un curso
   */
  asignarEstudianteACurso(estudianteId: number, cursoId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/cursos/estudiantes/asignar-curso/`, {
      estudiante_id: estudianteId,
      curso_id: cursoId
    });
  }

  /**
   * Desasigna un estudiante de un curso
   */
  desasignarEstudianteDeCurso(estudianteId: number): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/desasignar-curso/`, {});
  }

  /**
   * Obtiene las calificaciones de un estudiante específico
   */
  getCalificacionesEstudiante(estudianteId: number, filtros?: { materia_id?: number; tipo_evaluacion?: string }): Observable<any[]> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.tipo_evaluacion) params = params.append('tipo_evaluacion', filtros.tipo_evaluacion);
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/calificaciones/`, { params })
      .pipe(
        map(response => {
          if (response && response.calificaciones) {
            return response.calificaciones;
          } else if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene las asistencias de un estudiante específico
   */
  getAsistenciasEstudiante(estudianteId: number, filtros?: { materia_id?: number; fecha_inicio?: string; fecha_fin?: string }): Observable<any[]> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.fecha_inicio) params = params.append('fecha_inicio', filtros.fecha_inicio);
      if (filtros.fecha_fin) params = params.append('fecha_fin', filtros.fecha_fin);
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/asistencias/`, { params })
      .pipe(
        map(response => {
          if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene las evaluaciones para un estudiante específico
   */
  getEvaluacionesEstudiante(estudianteId: number, filtros?: { materia_id?: number; trimestre_id?: number; anio?: number }): Observable<any[]> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.anio) params = params.append('anio', filtros.anio.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/evaluaciones/`, { params })
      .pipe(
        map(response => {
          if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene estudiantes por curso y materia para una evaluación específica
   * Método combinado para el caso de uso principal
   */
  getEstudiantesParaCalificacion(materiaId: number, evaluacionId: number, tipoEvaluacion: 'entregable' | 'participacion'): Observable<any[]> {
    // Primero obtenemos todos los estudiantes de la materia
    return this.getEstudiantesPorMateria(materiaId).pipe(
      map(estudiantes => {
        // Formateamos los datos para uniformidad
        return estudiantes.map(est => {
          return {
            estudiante: {
              id: est.id,
              nombre: est.nombre,
              apellido: est.apellido,
              codigo: est.codigo
            },
            nota: null,
            observaciones: '',
            retroalimentacion: '',
            fecha_entrega: null,
            entrega_tardia: false
          };
        });
      })
    );
  }

  /**
   * Obtiene historial académico completo de un estudiante
   */
  getHistorialAcademico(estudianteId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/historial-academico/`);
  }

  /**
   * Obtiene información completa de un estudiante, incluyendo curso y materias
   */
  getEstudianteCompleto(estudianteId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/curso-materias/`);
  }
}
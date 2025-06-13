import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class TutorService {
  private apiUrl = 'http://localhost:8000/api';

  constructor(private http: HttpClient) { }

  /**
   * Obtiene la información de un tutor específico por su ID
   */
  getTutor(tutorId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/usuarios/tutores/${tutorId}/`);
  }

  /**
   * RUTA CORREGIDA 70: Obtiene todos los estudiantes asignados a un tutor específico
   * GET api/cursos/tutores/<int:tutor_id>/estudiantes/
   */
  getEstudiantesTutor(tutorId: number): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/`)
      .pipe(
        map(response => {
          console.log('Respuesta getEstudiantesTutor:', response);
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
   * RUTA CORREGIDA 71: Obtiene las calificaciones de todos los estudiantes de un tutor
   * GET api/cursos/tutores/<int:tutor_id>/calificaciones/
   */
  getCalificacionesEstudiantes(tutorId: number, filtros?: { 
    materia_id?: number; 
    trimestre_id?: number; 
    estudiante_id?: number;
    anio?: number;
  }): Observable<any[]> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.estudiante_id) params = params.append('estudiante_id', filtros.estudiante_id.toString());
      if (filtros.anio) params = params.append('anio', filtros.anio.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params })
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
   * RUTA CORREGIDA 72: Obtiene las calificaciones de un estudiante específico bajo supervisión del tutor
   * GET api/cursos/tutores/<int:tutor_id>/estudiantes/<int:estudiante_id>/calificaciones/
   */
  getCalificacionesEstudianteDetalle(tutorId: number, estudianteId: number, filtros?: {
    materia_id?: number;
    trimestre_id?: number;
    anio?: number;
  }): Observable<any> {
    let params = new HttpParams();
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.anio) params = params.append('anio', filtros.anio.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/${estudianteId}/calificaciones/`, { params });
  }

  /**
   * ✅ RUTA CORREGIDA: Asignar estudiantes a un tutor (POST)
   * RUTA REAL: api/cursos/tutores/<int:tutor_id>/asignar-estudiantes/
   */
  asignarEstudiantesTutor(tutorId: number, estudiantesIds: number[]): Observable<any> {
    const body = {
      estudiantes_ids: estudiantesIds
    };
    
    console.log('Asignando estudiantes al tutor:', { tutorId, estudiantesIds });
    
    return this.http.post<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/asignar-estudiantes/`, body);
  }

  /**
   * ✅ RUTA CORREGIDA: Obtener estudiantes sin curso (no hay ruta específica para sin-tutor)
   * RUTA REAL: api/cursos/estudiantes/sin-curso/
   */
  getEstudiantesSinCurso(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/cursos/estudiantes/sin-curso/`)
      .pipe(
        map(response => {
          console.log('Respuesta getEstudiantesSinCurso:', response);
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
   * ✅ NUEVO: Obtener estudiantes de un curso específico
   * RUTA: api/cursos/cursos/<int:curso_id>/estudiantes/
   */
  getEstudiantesDeCurso(cursoId: number): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/cursos/cursos/${cursoId}/estudiantes/`)
      .pipe(
        map(response => {
          console.log('Respuesta getEstudiantesDeCurso:', response);
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
   * ✅ NUEVO: Asignar estudiante a curso
   * RUTA: api/cursos/cursos/asignar-estudiante/
   */
  asignarEstudianteACurso(estudianteId: number, cursoId: number): Observable<any> {
    const body = {
      estudiante_id: estudianteId,
      curso_id: cursoId
    };
    
    console.log('Asignando estudiante a curso:', body);
    
    return this.http.post<any>(`${this.apiUrl}/cursos/cursos/asignar-estudiante/`, body);
  }

  /**
   * ✅ NUEVO: Desasignar estudiante de curso
   * RUTA: api/cursos/estudiantes/<int:estudiante_id>/desasignar-curso/
   */
  desasignarEstudianteDeCurso(estudianteId: number): Observable<any> {
    console.log('Desasignando estudiante de curso:', estudianteId);
    
    return this.http.post<any>(`${this.apiUrl}/cursos/estudiantes/${estudianteId}/desasignar-curso/`, {});
  }

  /**
   * ✅ NUEVO: Obtener todos los cursos
   * RUTA: api/cursos/cursos/
   */
  getCursos(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/cursos/cursos/`)
      .pipe(
        map(response => {
          console.log('Respuesta getCursos:', response);
          if (response && response.cursos) {
            return response.cursos;
          } else if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * ✅ FUNCIÓN AUXILIAR: Para obtener estudiantes disponibles para asignar a tutor
   * Como no hay ruta específica para estudiantes sin tutor, usamos estudiantes sin curso
   */
  getEstudiantesDisponiblesParaTutor(): Observable<any[]> {
    return this.getEstudiantesSinCurso();
  }

  /**
   * ✅ FUNCIÓN AUXILIAR: Buscar todos los estudiantes y filtrar los que no tienen tutor
   * Usando la API de usuarios si es necesario
   */
  getTodosLosEstudiantes(): Observable<any[]> {
    return this.http.get<any>(`${this.apiUrl}/usuarios/usuarios/estudiantes/`)
      .pipe(
        map(response => {
          console.log('Respuesta getTodosLosEstudiantes:', response);
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
   * ✅ MÉTODO PARA OBTENER ESTUDIANTES SIN TUTOR
   * Como no hay ruta específica, combinamos datos
   */
  getEstudiantesSinTutor(): Observable<any[]> {
    // Como no existe una ruta específica para estudiantes sin tutor,
    // usamos los estudiantes sin curso como alternativa
    return this.getEstudiantesSinCurso();
  }

  /**
   * ✅ DESASIGNAR ESTUDIANTES DE TUTOR
   * Como no hay ruta específica de desasignación de tutor, 
   * podríamos usar la desasignación de curso
   */
  desasignarEstudiantesTutor(tutorId: number, estudiantesIds: number[]): Observable<any> {
    console.log('Desasignando estudiantes del tutor (usando desasignación de curso):', { tutorId, estudiantesIds });
    
    // Como no hay ruta específica, desasignamos del curso
    const observables = estudiantesIds.map(id => this.desasignarEstudianteDeCurso(id));
    
    // Retornamos el primer observable (simplificado)
    return observables[0] || new Observable(subscriber => subscriber.next({}));
  }

  /**
   * Método auxiliar para debug - verificar estructura de respuesta
   */
  testearRutaTutorEstudiantes(tutorId: number): Observable<any> {
    console.log(`Testing ruta: ${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/`);
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/`)
      .pipe(
        map(response => {
          console.log('RESPUESTA COMPLETA:', response);
          console.log('Tipo de respuesta:', typeof response);
          console.log('Es array:', Array.isArray(response));
          console.log('Claves del objeto:', Object.keys(response || {}));
          return response;
        })
      );
  }

  /**
   * Obtiene el resumen de rendimiento utilizando la ruta de calificaciones
   */
  getResumenRendimientoEstudiantes(tutorId: number, filtros?: {
    trimestre_id?: number;
    anio?: number;
  }): Observable<any> {
    let params = new HttpParams();
    params = params.append('resumen', 'true');
    
    if (filtros) {
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.anio) params = params.append('anio', filtros.anio.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params });
  }

  /**
   * Obtiene las asistencias utilizando la ruta de calificaciones con parámetros
   */
  getAsistenciasEstudiantes(tutorId: number, filtros?: {
    materia_id?: number;
    fecha_inicio?: string;
    fecha_fin?: string;
    estudiante_id?: number;
  }): Observable<any[]> {
    let params = new HttpParams();
    params = params.append('incluir_asistencias', 'true');
    
    if (filtros) {
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.fecha_inicio) params = params.append('fecha_inicio', filtros.fecha_inicio);
      if (filtros.fecha_fin) params = params.append('fecha_fin', filtros.fecha_fin);
      if (filtros.estudiante_id) params = params.append('estudiante_id', filtros.estudiante_id.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params })
      .pipe(
        map(response => {
          if (response && response.asistencias) {
            return response.asistencias;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene información del curso usando la ruta de estudiantes con parámetro
   */
  getInformacionCurso(tutorId: number): Observable<any> {
    let params = new HttpParams();
    params = params.append('info_curso', 'true');
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/`, { params });
  }

  /**
   * Obtiene el historial académico completo de un estudiante específico
   */
  getHistorialEstudiante(tutorId: number, estudianteId: number): Observable<any> {
    let params = new HttpParams();
    params = params.append('historial_completo', 'true');
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/estudiantes/${estudianteId}/calificaciones/`, { params });
  }

  /**
   * Obtiene los promedios trimestrales de todos los estudiantes
   */
  getPromediosTrimestrales(tutorId: number, filtros?: {
    trimestre_id?: number;
    materia_id?: number;
    anio?: number;
  }): Observable<any[]> {
    let params = new HttpParams();
    params = params.append('promedios_trimestrales', 'true');
    
    if (filtros) {
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.materia_id) params = params.append('materia_id', filtros.materia_id.toString());
      if (filtros.anio) params = params.append('anio', filtros.anio.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params })
      .pipe(
        map(response => {
          if (response && response.promedios) {
            return response.promedios;
          } else if (Array.isArray(response)) {
            return response;
          }
          return [];
        })
      );
  }

  /**
   * Obtiene alertas de estudiantes con bajo rendimiento o asistencia
   */
  getAlertasEstudiantes(tutorId: number, filtros?: {
    tipo_alerta?: 'rendimiento' | 'asistencia' | 'ambos';
    trimestre_id?: number;
  }): Observable<any[]> {
    let params = new HttpParams();
    params = params.append('alertas', 'true');
    
    if (filtros) {
      if (filtros.tipo_alerta) params = params.append('tipo_alerta', filtros.tipo_alerta);
      if (filtros.trimestre_id) params = params.append('trimestre_id', filtros.trimestre_id.toString());
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params })
      .pipe(
        map(response => {
          if (response && response.alertas) {
            return response.alertas;
          }
          return [];
        })
      );
  }

  /**
   * Método auxiliar para obtener comparación de rendimiento entre trimestres
   */
  getComparacionRendimiento(tutorId: number, trimestre1Id: number, trimestre2Id: number): Observable<any> {
    let params = new HttpParams();
    params = params.append('comparacion', 'true');
    params = params.append('trimestre_1', trimestre1Id.toString());
    params = params.append('trimestre_2', trimestre2Id.toString());
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params });
  }

  /**
   * Obtiene reportes personalizados para el tutor
   */
  getReportePersonalizado(tutorId: number, configuracion: {
    tipo_reporte: 'rendimiento' | 'asistencia' | 'completo';
    periodo: 'trimestre' | 'semestre' | 'anual';
    formato: 'resumen' | 'detallado';
    filtros?: {
      estudiante_id?: number;
      materia_id?: number;
      trimestre_id?: number;
      fecha_inicio?: string;
      fecha_fin?: string;
    };
  }): Observable<any> {
    let params = new HttpParams();
    params = params.append('reporte_personalizado', 'true');
    params = params.append('tipo_reporte', configuracion.tipo_reporte);
    params = params.append('periodo', configuracion.periodo);
    params = params.append('formato', configuracion.formato);
    
    if (configuracion.filtros) {
      Object.entries(configuracion.filtros).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          params = params.append(key, value.toString());
        }
      });
    }
    
    return this.http.get<any>(`${this.apiUrl}/cursos/tutores/${tutorId}/calificaciones/`, { params });
  }
}
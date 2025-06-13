import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { ApiConfig } from '../config/api-config';

@Injectable({
  providedIn: 'root'
})
export class EvaluacionesService {
  private apiUrl = ApiConfig.ENDPOINTS.CURSOS;

  constructor(private http: HttpClient) { }

  // =================== TIPOS DE EVALUACIÓN ===================

  /**
   * Obtiene todos los tipos de evaluación disponibles
   */
  getTiposEvaluacion(): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/tipos-evaluacion/`);
  }

  /**
   * Obtiene los detalles de un tipo de evaluación específico
   */
  getTipoEvaluacion(tipoId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/tipos-evaluacion/${tipoId}/`);
  }

  /**
   * Crea un nuevo tipo de evaluación
   */
  createTipoEvaluacion(tipoData: {
    nombre: string;
    descripcion: string;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/tipos-evaluacion/create/`, tipoData);
  }

  /**
   * Actualiza un tipo de evaluación existente
   */
  updateTipoEvaluacion(tipoId: number, tipoData: {
    descripcion?: string;
    activo?: boolean;
  }): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/tipos-evaluacion/${tipoId}/update/`, tipoData);
  }

  /**
   * Elimina (desactiva) un tipo de evaluación
   */
  deleteTipoEvaluacion(tipoId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/tipos-evaluacion/${tipoId}/delete/`);
  }

  // =================== EVALUACIONES ===================

  /**
   * Crea una nueva evaluación (entregable o participación)
   */
  createEvaluacion(evaluacionData: {
    materia_id: number;
    tipo_evaluacion_id: number;
    trimestre_id: number;
    titulo: string;
    descripcion?: string;
    porcentaje_nota_final: number;
    publicado?: boolean;
    
    // Para evaluaciones entregables
    fecha_asignacion?: string;
    fecha_entrega?: string;
    fecha_limite?: string;
    nota_maxima?: number;
    nota_minima_aprobacion?: number;
    permite_entrega_tardia?: boolean;
    penalizacion_tardio?: number;
    
    // Para evaluaciones de participación
    fecha_registro?: string;
    criterios_participacion?: string;
    escala_calificacion?: string;
  }): Observable<any> {
    console.log('Enviando datos de evaluación:', evaluacionData);
    return this.http.post<any>(`${this.apiUrl}/evaluaciones/create/`, evaluacionData);
  }

  /**
   * Obtiene los detalles de una evaluación específica
   */
  getEvaluacion(evaluacionId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/evaluaciones/${evaluacionId}/`);
  }

  /**
   * Actualiza una evaluación existente
   */
  updateEvaluacion(evaluacionId: number, evaluacionData: {
    titulo?: string;
    descripcion?: string;
    porcentaje_nota_final?: number;
    publicado?: boolean;
    
    // Para evaluaciones entregables
    fecha_entrega?: string;
    fecha_limite?: string;
    nota_maxima?: number;
    nota_minima_aprobacion?: number;
    permite_entrega_tardia?: boolean;
    penalizacion_tardio?: number;
    
    // Para evaluaciones de participación
    fecha_registro?: string;
    criterios_participacion?: string;
    escala_calificacion?: string;
  }): Observable<any> {
    return this.http.put<any>(`${this.apiUrl}/evaluaciones/${evaluacionId}/update/`, evaluacionData);
  }

  /**
   * Elimina (desactiva) una evaluación
   */
  deleteEvaluacion(evaluacionId: number): Observable<any> {
    return this.http.delete<any>(`${this.apiUrl}/evaluaciones/${evaluacionId}/delete/`);
  }

  /**
   * Obtiene todas las evaluaciones de una materia específica
   */
  getEvaluacionesPorMateria(materiaId: number, filtros?: {
    tipo_evaluacion_id?: number;
    trimestre_id?: number;
    publicado?: boolean;
    activo?: boolean;
  }): Observable<any> {
    let url = `${this.apiUrl}/materias/${materiaId}/evaluaciones/`;
    
    if (filtros) {
      const params = new URLSearchParams();
      if (filtros.tipo_evaluacion_id) params.append('tipo_evaluacion_id', filtros.tipo_evaluacion_id.toString());
      if (filtros.trimestre_id) params.append('trimestre_id', filtros.trimestre_id.toString());
      if (filtros.publicado !== undefined) params.append('publicado', filtros.publicado.toString());
      if (filtros.activo !== undefined) params.append('activo', filtros.activo.toString());
      
      const queryString = params.toString();
      if (queryString) {
        url += '?' + queryString;
      }
    }
    
    return this.http.get<any>(url);
  }

  // =================== MÉTODOS AUXILIARES ===================

  /**
   * Valida los datos de una evaluación antes de enviarlos
   */
  validarDatosEvaluacion(evaluacionData: any): { valido: boolean; errores: string[] } {
    const errores: string[] = [];

    // Validaciones básicas
    if (!evaluacionData.materia_id) errores.push('La materia es requerida');
    if (!evaluacionData.tipo_evaluacion_id) errores.push('El tipo de evaluación es requerido');
    if (!evaluacionData.trimestre_id) errores.push('El trimestre es requerido');
    if (!evaluacionData.titulo || evaluacionData.titulo.trim() === '') errores.push('El título es requerido');
    if (!evaluacionData.porcentaje_nota_final || evaluacionData.porcentaje_nota_final <= 0) {
      errores.push('El porcentaje de la nota final debe ser mayor a 0');
    }
    if (evaluacionData.porcentaje_nota_final > 100) {
      errores.push('El porcentaje de la nota final no puede ser mayor a 100');
    }

    // Validaciones para evaluaciones entregables
    if (evaluacionData.fecha_asignacion && evaluacionData.fecha_entrega) {
      const fechaAsignacion = new Date(evaluacionData.fecha_asignacion);
      const fechaEntrega = new Date(evaluacionData.fecha_entrega);
      
      if (fechaEntrega < fechaAsignacion) {
        errores.push('La fecha de entrega no puede ser anterior a la fecha de asignación');
      }

      if (evaluacionData.fecha_limite) {
        const fechaLimite = new Date(evaluacionData.fecha_limite);
        if (fechaLimite < fechaEntrega) {
          errores.push('La fecha límite no puede ser anterior a la fecha de entrega');
        }
      }
    }

    // Validaciones de notas
    if (evaluacionData.nota_maxima && evaluacionData.nota_minima_aprobacion) {
      if (evaluacionData.nota_minima_aprobacion > evaluacionData.nota_maxima) {
        errores.push('La nota mínima de aprobación no puede ser mayor que la nota máxima');
      }
    }

    return {
      valido: errores.length === 0,
      errores
    };
  }

  /**
   * Formatea las fechas para envío al backend
   */
  formatearFechaParaBackend(fecha: string | Date): string {
    if (!fecha) return '';
    
    const fechaObj = typeof fecha === 'string' ? new Date(fecha) : fecha;
    return fechaObj.toISOString().split('T')[0]; // YYYY-MM-DD
  }

  /**
   * Determina si una evaluación está vencida
   */
  estaVencida(fechaEntrega: string): boolean {
    if (!fechaEntrega) return false;
    
    const hoy = new Date();
    const fechaVencimiento = new Date(fechaEntrega);
    
    return fechaVencimiento < hoy;
  }

  /**
   * Calcula los días restantes hasta la fecha de entrega
   */
  diasRestantes(fechaEntrega: string): number {
    if (!fechaEntrega) return 0;
    
    const hoy = new Date();
    const fechaVencimiento = new Date(fechaEntrega);
    const diferencia = fechaVencimiento.getTime() - hoy.getTime();
    
    return Math.ceil(diferencia / (1000 * 3600 * 24));
  }

  /**
   * Obtiene el estado de una evaluación basado en las fechas
   */
  getEstadoEvaluacion(evaluacion: any): {
    estado: 'pendiente' | 'proximaVencimiento' | 'vencida' | 'completada';
    mensaje: string;
    color: string;
  } {
    if (!evaluacion.fecha_entrega) {
      return {
        estado: 'pendiente',
        mensaje: 'Sin fecha de entrega',
        color: 'gray'
      };
    }

    const diasRestantes = this.diasRestantes(evaluacion.fecha_entrega);
    
    if (diasRestantes < 0) {
      return {
        estado: 'vencida',
        mensaje: `Vencida hace ${Math.abs(diasRestantes)} días`,
        color: 'red'
      };
    } else if (diasRestantes <= 3) {
      return {
        estado: 'proximaVencimiento',
        mensaje: `Vence en ${diasRestantes} días`,
        color: 'orange'
      };
    } else {
      return {
        estado: 'pendiente',
        mensaje: `${diasRestantes} días restantes`,
        color: 'green'
      };
    }
  }

  /**
   * Formatea el tipo de evaluación para mostrar
   */
  formatearTipoEvaluacion(tipo: any): string {
    if (!tipo) return '';
    
    return tipo.nombre_display || tipo.nombre || '';
  }

  /**
   * Configura el porcentaje máximo permitido para un tipo de evaluación en una materia
   */
  configurarPorcentajeEvaluacion(configuracion: {
    materia_id: number;
    tipo_evaluacion_id: number;
    porcentaje: number;
  }): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/configuracion-evaluacion/`, configuracion);
  }

  /**
   * Obtiene la configuración de porcentajes máximos por tipo de evaluación para una materia
   */
  getConfiguracionPorcentajes(materiaId: number): Observable<any> {
    return this.http.get<any>(`${this.apiUrl}/materias/${materiaId}/configuracion-evaluacion/`);
  }

  /**
   * Verifica si el porcentaje de una nueva evaluación excede el máximo configurado
   */
  verificarPorcentajeDisponible(
    materiaId: number, 
    tipoEvaluacionId: number, 
    porcentajeRequerido: number,
    evaluacionesActuales: any[]
  ): Observable<{
    disponible: boolean;
    porcentajeMaximo: number;
    porcentajeUsado: number;
    porcentajeDisponible: number;
    mensaje: string;
  }> {
    // Asegurarse de que los parámetros sean números
    materiaId = Number(materiaId);
    tipoEvaluacionId = Number(tipoEvaluacionId);
    porcentajeRequerido = Number(porcentajeRequerido);
    
    return this.getConfiguracionPorcentajes(materiaId).pipe(
      map((configuraciones: any) => {
        // Buscar la configuración para este tipo de evaluación
        const config = Array.isArray(configuraciones) 
          ? configuraciones.find((c: any) => c.tipo_evaluacion_id === tipoEvaluacionId) 
          : null;
        
        // Si no hay configuración, usar valor predeterminado de 100%
        const porcentajeMaximo = config ? config.porcentaje : 100;
        
        // Calcular porcentaje ya usado
        const porcentajeUsado = this.calcularPorcentajeUsado(
          evaluacionesActuales,
          tipoEvaluacionId
        );
        
        const porcentajeDisponible = porcentajeMaximo - porcentajeUsado;
        const disponible = porcentajeRequerido <= porcentajeDisponible;
        
        return {
          disponible,
          porcentajeMaximo,
          porcentajeUsado,
          porcentajeDisponible,
          mensaje: disponible 
            ? `Porcentaje disponible: ${porcentajeDisponible}%`
            : `El porcentaje excede el máximo disponible (${porcentajeDisponible}%)`
        };
      })
    );
  }

  /**
   * Calcula el porcentaje total usado por tipo de evaluación
   */
  calcularPorcentajeUsado(evaluaciones: any[], tipoEvaluacionId: number): number {
    return evaluaciones
      .filter(evaluacion => evaluacion.tipo_evaluacion?.id === tipoEvaluacionId)
      .reduce((total, evaluacion) => total + (evaluacion.porcentaje_nota_final || 0), 0);
  }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormArray } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MateriasService } from '../../../services/materias.service';
import { EvaluacionesService } from '../../../services/evaluaciones.service';
import { CalificacionesService } from '../../../services/calificaciones.service';
import { UsuariosService } from '../../../services/usuarios.service';
import { AuthService } from '../../../services/auth.service';
import { EstudiantesService } from '../../../services/estudiantes.service';

@Component({
  selector: 'app-calificaciones',
  templateUrl: './calificaciones.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class CalificacionesComponent implements OnInit {
  // Información de la evaluación
  evaluacionId: number | null = null;
  // Cambia la definición de tipo aquí
  tipoEvaluacion: 'entregable' | 'participacion' = 'entregable';
  evaluacion: any = null;
  
  // Datos para las calificaciones
  estudiantes: any[] = [];
  calificaciones: any[] = [];
  
  // Estado de carga
  cargandoEvaluacion: boolean = false;
  cargandoEstudiantes: boolean = false;
  guardandoCalificaciones: boolean = false;
  
  // Formularios
  calificacionForm: FormGroup;
  calificacionMasivaForm: FormGroup;
  
  // Control de errores y mensajes
  error: string = '';
  mensaje: string = '';
  
  // Modo de calificación
  modoEdicion: boolean = false;
  modoCalificacionIndividual: boolean = false;
  estudianteSeleccionado: any = null;
  
  // Estadísticas
  estadisticas: any = {
    calificados: 0,
    pendientes: 0,
    promedioActual: 0
  };

  // Añadir esta propiedad para usar en la plantilla
  Math = Math;

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private router: Router,
    private materiasService: MateriasService,
    private evaluacionesService: EvaluacionesService,
    private calificacionesService: CalificacionesService,
    private estudiantesService: EstudiantesService, // Agregar este servicio
    private usuariosService: UsuariosService,
    private authService: AuthService
  ) {
    this.calificacionForm = this.fb.group({
      estudiante_id: ['', Validators.required],
      nota: ['', [Validators.required, Validators.min(0), Validators.max(100)]],
      observaciones: [''],
      retroalimentacion: ['']
    });
    
    this.calificacionMasivaForm = this.fb.group({
      calificaciones: this.fb.array([])
    });
  }

  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.evaluacionId = +params['id'];
        
        this.route.queryParams.subscribe(queryParams => {
          if (queryParams['tipo']) {
            // Aquí valida el tipo antes de asignarlo
            const tipo = queryParams['tipo'];
            if (tipo === 'entregable' || tipo === 'participacion') {
              this.tipoEvaluacion = tipo;
            }
          }
          
          this.cargarEvaluacion();
        });
      } else {
        this.error = 'No se ha especificado una evaluación válida';
      }
    });
  }
  
  /**
   * Carga los datos de la evaluación seleccionada
   */
  cargarEvaluacion(): void {
    if (!this.evaluacionId) return;
    
    this.cargandoEvaluacion = true;
    this.error = '';
    
    this.evaluacionesService.getEvaluacion(this.evaluacionId).subscribe({
      next: (response: any) => {
        // Asumiendo que la evaluación viene en la respuesta directamente o en un campo evaluacion
        this.evaluacion = response.evaluacion || response;
        console.log('Datos de la evaluación:', this.evaluacion);
        this.cargandoEvaluacion = false;
        
        // Cargar calificaciones existentes
        this.cargarCalificaciones();
      },
      error: (error) => {
        console.error('Error al cargar evaluación:', error);
        this.error = 'Error al cargar los datos de la evaluación';
        this.cargandoEvaluacion = false;
      }
    });
  }
  
  /**
   * Carga las calificaciones existentes para esta evaluación
   */
  cargarCalificaciones(): void {
    if (!this.evaluacionId) return;
    
    this.cargandoEstudiantes = true;
    
    // Ya no necesitamos cargar la evaluación nuevamente, pues ya la tenemos en this.evaluacion
    // No hay necesidad de llamar a getEvaluacion() otra vez

    // Aseguramos que evaluacionId es number en este punto
    const evaluacionId: number = this.evaluacionId;
    const materiaId = this.evaluacion?.materia?.id;

    if (!materiaId) {
      console.error('La evaluación no tiene una materia asociada');
      this.error = 'Error: La evaluación no tiene una materia asociada';
      this.cargandoEstudiantes = false;
      return;
    }
    
    // Ahora obtenemos los estudiantes y sus calificaciones directamente
    this.estudiantesService.getEstudiantesParaCalificacion(
      materiaId, 
      evaluacionId, 
      this.tipoEvaluacion
    ).subscribe({
      next: (estudiantes: any[]) => {
        console.log('Estudiantes para calificar:', estudiantes);
        
        // Ahora obtenemos las calificaciones existentes
        this.calificacionesService.getCalificacionesPorEvaluacion(evaluacionId, this.tipoEvaluacion).subscribe({
          next: (response: any) => {
            console.log('Calificaciones existentes:', response);
            
            // Combinar estudiantes con calificaciones existentes
            if (response && response.calificaciones && response.calificaciones.length > 0) {
              // Si hay calificaciones, usamos esos datos
              this.estudiantes = response.calificaciones;
              this.calificaciones = this.estudiantes.map(est => ({
                estudiante_id: est.estudiante?.id,
                nombre: `${est.estudiante?.nombre} ${est.estudiante?.apellido}`,
                nota: est.nota,
                observaciones: est.observaciones || '',
                retroalimentacion: est.retroalimentacion || '',
                fecha_entrega: est.fecha_entrega,
                entrega_tardia: est.entrega_tardia
              }));
            } else {
              // Si no hay calificaciones, usamos la lista de estudiantes de la materia
              this.estudiantes = estudiantes;
              this.calificaciones = estudiantes.map(est => ({
                estudiante_id: est.estudiante.id,
                nombre: `${est.estudiante.nombre} ${est.estudiante.apellido}`,
                nota: est.nota,
                observaciones: est.observaciones || '',
                retroalimentacion: est.retroalimentacion || '',
                fecha_entrega: null,
                entrega_tardia: false
              }));
            }
            
            this.actualizarFormularioMasivo();
            this.calcularEstadisticas();
            this.cargandoEstudiantes = false;
          },
          error: (error) => {
            console.error('Error al cargar calificaciones:', error);
            
            // Si falla, usamos la lista de estudiantes sin calificaciones
            this.estudiantes = estudiantes;
            this.calificaciones = estudiantes.map(est => ({
              estudiante_id: est.estudiante.id,
              nombre: `${est.estudiante.nombre} ${est.estudiante.apellido}`,
              nota: null,
              observaciones: '',
              retroalimentacion: '',
              fecha_entrega: null,
              entrega_tardia: false
            }));
            
            this.actualizarFormularioMasivo();
            this.calcularEstadisticas();
            this.cargandoEstudiantes = false;
          }
        });
      },
      error: (error) => {
        console.error('Error al cargar estudiantes para la evaluación:', error);
        this.error = 'Error al cargar los estudiantes';
        this.cargandoEstudiantes = false;
        
        // En caso de error, cargar datos simulados para pruebas
        this.cargarDatosSimulados();
      }
    });
  }
  
  /**
   * Inicializa el formulario de calificaciones masivas
   */
  actualizarFormularioMasivo(): void {
    const calificacionesArray = this.calificacionMasivaForm.get('calificaciones') as FormArray;
    calificacionesArray.clear();
    
    this.calificaciones.forEach(cal => {
      calificacionesArray.push(this.fb.group({
        estudiante_id: [cal.estudiante_id],
        nombre: [cal.nombre],
        nota: [cal.nota, [Validators.min(0), Validators.max(100)]],
        observaciones: [cal.observaciones || ''],
        retroalimentacion: [cal.retroalimentacion || '']
      }));
    });
  }
  
  /**
   * Obtener el array de calificaciones del formulario
   */
  get calificacionesArray(): FormArray {
    return this.calificacionMasivaForm.get('calificaciones') as FormArray;
  }
  
  /**
   * Cargar datos simulados para pruebas
   */
  cargarDatosSimulados(): void {
    this.estudiantes = [
      { id: 1, nombre: 'Juan', apellido: 'Pérez', nota: null },
      { id: 2, nombre: 'María', apellido: 'García', nota: 85 },
      { id: 3, nombre: 'Carlos', apellido: 'López', nota: 70 }
    ];
    
    this.calificaciones = this.estudiantes.map(est => ({
      estudiante_id: est.id,
      nombre: `${est.nombre} ${est.apellido}`,
      nota: est.nota,
      observaciones: '',
      retroalimentacion: ''
    }));
    
    this.actualizarFormularioMasivo();
    this.calcularEstadisticas();
  }
  
  /**
   * Calcula las estadísticas de calificaciones
   */
  calcularEstadisticas(): void {
    const calificados = this.calificaciones.filter(c => c.nota !== null && c.nota !== undefined);
    const total = this.calificaciones.length;
    
    let suma = 0;
    calificados.forEach(c => suma += c.nota);
    
    this.estadisticas = {
      calificados: calificados.length,
      pendientes: total - calificados.length,
      promedioActual: calificados.length > 0 ? Math.round((suma / calificados.length) * 100) / 100 : 0
    };
  }
  
  /**
   * Guarda las calificaciones ingresadas
   */
  guardarCalificaciones(): void {
    if (this.calificacionMasivaForm.invalid) {
      this.marcarCamposInvalidos();
      return;
    }
    
    if (!this.evaluacionId) {
      this.error = 'No hay una evaluación válida seleccionada';
      return;
    }
    
    // Ahora TypeScript sabe que this.evaluacionId es number
    
    this.guardandoCalificaciones = true;
    this.error = '';
    this.mensaje = '';
    
    const calificacionesValidas = this.calificacionesArray.value
      .filter((c: any) => c.nota !== null && c.nota !== undefined && c.nota !== '');
    
    if (calificacionesValidas.length === 0) {
      this.error = 'No hay calificaciones para guardar';
      this.guardandoCalificaciones = false;
      return;
    }
    
    // Como validamos que evaluacionId no es null, podemos proceder:
    const evaluacionIdSeguro = this.evaluacionId;
    
    // Preparar datos para enviar al servidor
    const datosParaEnviar = {
      evaluacion_id: evaluacionIdSeguro,
      tipo_evaluacion: this.tipoEvaluacion,
      calificaciones: calificacionesValidas
    };
    
    console.log('Enviando calificaciones:', datosParaEnviar);
    
    this.calificacionesService.registrarCalificacionesMasivo(datosParaEnviar).subscribe({
      next: (response) => {
        console.log('Respuesta de guardar calificaciones:', response);
        this.mensaje = 'Calificaciones guardadas correctamente';
        this.guardandoCalificaciones = false;
        
        // Recargar datos
        this.cargarCalificaciones();
      },
      error: (error) => {
        console.error('Error al guardar calificaciones:', error);
        this.error = error.error?.error || 'Error al guardar las calificaciones';
        this.guardandoCalificaciones = false;
      }
    });
  }
  
  /**
   * Guarda una calificación individual
   */
  guardarCalificacionIndividual(): void {
    if (this.calificacionForm.invalid || !this.evaluacionId) {
      Object.keys(this.calificacionForm.controls).forEach(key => {
        this.calificacionForm.get(key)?.markAsTouched();
      });
      return;
    }
    
    const datos = {
      evaluacion_id: this.evaluacionId,  // Esto ahora es seguro porque validamos arriba
      estudiante_id: this.calificacionForm.value.estudiante_id,
      tipo_evaluacion: this.tipoEvaluacion as 'entregable' | 'participacion',
      nota: this.calificacionForm.value.nota,
      observaciones: this.calificacionForm.value.observaciones,
      retroalimentacion: this.calificacionForm.value.retroalimentacion
    };
    
    this.guardandoCalificaciones = true;
    
    this.calificacionesService.registrarCalificacion(datos).subscribe({
      next: (response) => {
        console.log('Calificación guardada:', response);
        this.mensaje = 'Calificación guardada correctamente';
        this.guardandoCalificaciones = false;
        this.modoCalificacionIndividual = false;
        
        // Recargar calificaciones
        this.cargarCalificaciones();
      },
      error: (error) => {
        console.error('Error al guardar calificación:', error);
        this.error = error.error?.error || 'Error al guardar la calificación';
        this.guardandoCalificaciones = false;
      }
    });
  }
  
  /**
   * Marca todos los campos como tocados para mostrar validaciones
   */
  marcarCamposInvalidos(): void {
    const calificacionesArray = this.calificacionMasivaForm.get('calificaciones') as FormArray;
    
    for (let i = 0; i < calificacionesArray.length; i++) {
      const formGroup = calificacionesArray.at(i) as FormGroup;
      Object.keys(formGroup.controls).forEach(key => {
        const control = formGroup.get(key);
        if (control) {
          control.markAsTouched();
        }
      });
    }
  }
  
  /**
   * Vuelve a la página de evaluaciones
   */
  volver(): void {
    this.router.navigate(['/profesor/evaluaciones']);
  }

  /**
   * Cambia el tipo de vista (edición o solo lectura)
   */
  toggleModoEdicion(): void {
    this.modoEdicion = !this.modoEdicion;
  }

  /**
   * Vuelve al modo de calificación masiva
   */
  volverACalificacionMasiva(): void {
    this.modoCalificacionIndividual = false;
    this.estudianteSeleccionado = null;
  }

  /**
   * Valida si una nota está en el rango permitido
   */
  validarNota(event: any): void {
    const input = event.target;
    let valor = parseFloat(input.value);
    
    const notaMaxima = this.evaluacion?.nota_maxima || 100;
    
    if (isNaN(valor)) {
      input.value = '';
    } else if (valor < 0) {
      input.value = 0;
    } else if (valor > notaMaxima) {
      input.value = notaMaxima;
    }
  }

  /**
   * Activa el modo de calificación individual para un estudiante
   */
  calificarEstudiante(estudiante: any): void {
    this.estudianteSeleccionado = estudiante;
    this.modoCalificacionIndividual = true;
    
    // Buscar calificación existente para este estudiante
    const calificacionExistente = this.calificaciones.find(c => c.estudiante_id === estudiante.id);
    
    this.calificacionForm.patchValue({
      estudiante_id: estudiante.id,
      nota: calificacionExistente?.nota ?? '',
      observaciones: calificacionExistente?.observaciones ?? '',
      retroalimentacion: calificacionExistente?.retroalimentacion ?? ''
    });
  }

  /**
   * Obtiene el color representativo según la calificación
   */
  getColorPorNota(nota: number | null | undefined): string {
    if (nota === null || nota === undefined) return 'gray';
    return this.calificacionesService.getColorPorNota(
      nota, 
      this.evaluacion?.nota_minima_aprobacion || 51
    );
  }

  /**
   * Obtiene la escala cualitativa de una nota
   */
  getEscalaCualitativa(nota: number | null | undefined): string {
    if (nota === null || nota === undefined) return 'Sin calificar';
    return this.calificacionesService.getEscalaCualitativa(nota);
  }

  /**
   * Formatea una nota numérica para mostrar
   */
  formatearNota(nota: number | null | undefined): string {
    return this.calificacionesService.formatearNota(nota);
  }
}
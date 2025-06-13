import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';
import { EvaluacionesService } from '../../../services/evaluaciones.service';
import { ActivatedRoute } from '@angular/router';
import { TrimestreService } from '../../../services/trimestre.service';

interface Materia {
  id: number;
  nombre: string;
  curso_nombre?: string;
  curso?: any;
}

interface TrimestresResponse {
  trimestres: any[];
}

interface TipoEvaluacion {
  id: number;
  nombre: string;
  nombre_display: string;
  descripcion: string;
}

@Component({
  selector: 'app-evaluaciones',
  templateUrl: './evaluaciones.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterModule]
})
export class EvaluacionesComponent implements OnInit {
  // Lista de datos necesarios
  materias: Materia[] = [];
  tiposEvaluacion: TipoEvaluacion[] = [];
  trimestres: any[] = [];
  evaluaciones: any[] = [];
  
  // Estado de carga
  materiasLoading: boolean = false;
  tiposEvaluacionLoading: boolean = false;
  trimestresLoading: boolean = false;
  evaluacionesLoading: boolean = false;
  guardandoEvaluacion: boolean = false;

  // Formularios
  evaluacionForm: FormGroup;
  configuracionForm: FormGroup;
  
  // Control de errores y mensajes
  error: string = '';
  mensaje: string = '';
  
  // Flags de control
  mostrarFormulario: boolean = false;
  esEntregable: boolean = true;
  materiaSeleccionada: number | null = null;
  configurandoPorcentaje: boolean = false;
  
  // Datos del usuario
  usuario: any;

  // Configuración de porcentajes
  configuracionPorcentajes: any[] = [];

  // Propiedad para materia preseleccionada
  private materiaPreseleccionada: number | null = null;

  // Año actual
  private readonly anoActual: number = new Date().getFullYear();

  constructor(
    private fb: FormBuilder,
    private route: ActivatedRoute,
    private authService: AuthService,
    private materiasService: MateriasService,
    private evaluacionesService: EvaluacionesService,
    private trimestreService: TrimestreService, 
  ) {
    this.evaluacionForm = this.fb.group({
      materia_id: [null, Validators.required],
      tipo_evaluacion_id: [null, Validators.required],
      trimestre_id: [null, Validators.required],
      titulo: ['', Validators.required],
      descripcion: [''],
      porcentaje_nota_final: [10, [Validators.required, Validators.min(1), Validators.max(100)]],
      publicado: [false],
      
      // Campos para evaluaciones entregables
      fecha_asignacion: [this.obtenerFechaActual()],
      fecha_entrega: ['', Validators.required],
      fecha_limite: [''],
      nota_maxima: [100],
      nota_minima_aprobacion: [51],
      permite_entrega_tardia: [false],
      penalizacion_tardio: [0],
      
      // Campos para evaluaciones de participación
      fecha_registro: [this.obtenerFechaActual()],
      criterios_participacion: [''],
      escala_calificacion: ['NUMERICA']
    });
    
    this.configuracionForm = this.fb.group({
      materia_id: [null, Validators.required],
      tipo_evaluacion_id: [null, Validators.required],
      porcentaje: [10, [Validators.required, Validators.min(1), Validators.max(100)]]
    });
  }
  
  ngOnInit(): void {
    this.initializeFormDefaults();
    this.cargarDatos();
    
    // Detectar si hay una materia preseleccionada en los query params
    this.route.queryParams.subscribe(params => {
      if (params['materia']) {
        const materiaId = +params['materia'];
        console.log('Materia preseleccionada desde URL:', materiaId);
        
        // Esperar a que las materias se carguen antes de seleccionar
        if (this.materias.length > 0) {
          this.seleccionarMateriaAutomaticamente(materiaId);
        } else {
          // Si las materias no están cargadas aún, guardar el ID para seleccionar después
          this.materiaPreseleccionada = materiaId;
        }
      }
    });
  }

  // Método para inicializar los valores por defecto del formulario
  initializeFormDefaults(): void {
    // Obtener datos del usuario
    this.usuario = this.authService.getCurrentUser();
    console.log('Usuario actual:', this.usuario);
  }

  // Método para cargar todos los datos necesarios
  cargarDatos(): void {
    this.cargarMaterias();
    this.cargarTiposEvaluacion();
    this.cargarTrimestres();
  }

  obtenerFechaActual(): string {
    const hoy = new Date();
    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');
    return `${año}-${mes}-${dia}`;
  }

  // Método para verificar si una fecha pertenece al año actual
  private esDelAnoActual(fecha: string): boolean {
    if (!fecha) return false;
    const anoFecha = new Date(fecha).getFullYear();
    return anoFecha === this.anoActual;
  }

  // Método para filtrar trimestres del año actual
  private filtrarTrimestresAnoActual(trimestres: any[]): any[] {
    return trimestres.filter(trimestre => {
      // Verificar si la fecha de inicio o fin está en el año actual
      const fechaInicio = trimestre.fecha_inicio;
      const fechaFin = trimestre.fecha_fin;
      
      return this.esDelAnoActual(fechaInicio) || this.esDelAnoActual(fechaFin);
    });
  }

  // Método para filtrar evaluaciones del año actual
  private filtrarEvaluacionesAnoActual(evaluaciones: any[]): any[] {
    return evaluaciones.filter(evaluacion => {
      // Para evaluaciones entregables, verificar fecha_asignacion o fecha_entrega
      if (evaluacion.modelo === 'entregable') {
        return this.esDelAnoActual(evaluacion.fecha_asignacion) || 
               this.esDelAnoActual(evaluacion.fecha_entrega);
      }
      
      // Para evaluaciones de participación, verificar fecha_registro
      if (evaluacion.modelo === 'participacion') {
        return this.esDelAnoActual(evaluacion.fecha_registro);
      }

      // Si no tiene modelo específico, verificar fecha_creacion o created_at
      if (evaluacion.created_at) {
        return this.esDelAnoActual(evaluacion.created_at);
      }

      // Por defecto, mostrar si no se puede determinar la fecha
      return true;
    });
  }
  
  cargarMaterias(): void {
    this.materiasLoading = true;
    this.error = '';
    
    if (this.usuario && this.usuario.id) {
      this.materiasService.getMateriasPorProfesor(this.usuario.id).subscribe({
        next: (response: any) => {
          console.log('Respuesta de materias:', response);
          
          if (response && response.materias) {
            this.materias = response.materias;
          } else if (response && Array.isArray(response)) {
            this.materias = response;
          } else if (response && response.data && Array.isArray(response.data)) {
            this.materias = response.data;
          } else {
            console.warn('Formato de respuesta inesperado:', response);
            this.materias = [];
          }
          
          this.materiasLoading = false;
          
          // Si hay una materia preseleccionada, seleccionarla ahora que las materias están cargadas
          if (this.materiaPreseleccionada) {
            this.seleccionarMateriaAutomaticamente(this.materiaPreseleccionada);
            this.materiaPreseleccionada = null;
          }
          
          if (this.materias.length === 0) {
            this.error = 'No tienes materias asignadas';
          }
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar materias. Intenta nuevamente.';
          this.materiasLoading = false;
          
          // Fallback a datos simulados en caso de error
          this.cargarMateriasSimuladas();
        }
      });
    } else {
      this.materiasLoading = false;
      this.error = 'No se pudo identificar al profesor';
      this.cargarMateriasSimuladas();
    }
  }
  
  private seleccionarMateriaAutomaticamente(materiaId: number): void {
    const materiaEncontrada = this.materias.find(m => m.id === materiaId);
    if (materiaEncontrada) {
      // Actualizar el formulario con la materia seleccionada
      this.evaluacionForm.patchValue({
        materia_id: materiaId
      });
      
      // Actualizar la materia seleccionada
      this.materiaSeleccionada = materiaId;
      
      // Cargar las evaluaciones de esta materia
      this.cargarEvaluaciones(materiaId);
      
      console.log('Materia seleccionada automáticamente:', materiaEncontrada.nombre);
    } else {
      console.warn('No se encontró la materia con ID:', materiaId);
    }
  }
  
  cargarMateriasSimuladas(): void {
    setTimeout(() => {
      this.materias = [
        {
          id: 1,
          nombre: 'Matemáticas',
          curso: {
            id: 101,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 8,
            paralelo: 'A'
          },
          curso_nombre: 'Octavo A - Básica'
        },
        {
          id: 2,
          nombre: 'Lenguaje y Literatura',
          curso: {
            id: 101,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 8,
            paralelo: 'A'
          },
          curso_nombre: 'Octavo A - Básica'
        }
      ];
      this.materiasLoading = false;
    }, 500);
  }
  
  cargarTiposEvaluacion(): void {
    this.tiposEvaluacionLoading = true;
    
    this.evaluacionesService.getTiposEvaluacion().subscribe({
      next: (response: any) => {
        console.log('Tipos de evaluación:', response);
        
        if (response && response.tipos_evaluacion) {
          this.tiposEvaluacion = response.tipos_evaluacion;
        } else {
          this.tiposEvaluacion = [];
        }
        this.tiposEvaluacionLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar tipos de evaluación:', error);
        this.tiposEvaluacionLoading = false;
        
        // Fallback a datos simulados
        this.tiposEvaluacion = [
          { id: 1, nombre: 'TAREA', nombre_display: 'Tarea', descripcion: 'Tareas cortas' },
          { id: 2, nombre: 'EXAMEN', nombre_display: 'Examen', descripcion: 'Exámenes escritos' },
          { id: 3, nombre: 'PARTICIPACION', nombre_display: 'Participación', descripcion: 'Participación en clase' },
          { id: 4, nombre: 'PROYECTO', nombre_display: 'Proyecto', descripcion: 'Proyectos extensos' }
        ];
      }
    });
  }
  
  cargarTrimestres(): void {
    this.trimestresLoading = true;
    
    this.trimestreService.getTrimestresActuales().subscribe({
      next: (response: any) => {
        console.log('Trimestres originales:', response);
        
        let trimestresOriginales: any[] = [];
        
        if (response && response.trimestres) {
          trimestresOriginales = response.trimestres;
        } else if (Array.isArray(response)) {
          trimestresOriginales = response;
        } else {
          trimestresOriginales = [];
        }

        // Filtrar solo trimestres del año actual
        this.trimestres = this.filtrarTrimestresAnoActual(trimestresOriginales);
        
        console.log(`Trimestres filtrados para el año ${this.anoActual}:`, this.trimestres);
        
        this.trimestresLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar trimestres:', error);
        this.trimestresLoading = false;
        
        // Fallback a datos simulados del año actual
        const fechaActual = new Date();
        const anoActual = fechaActual.getFullYear();
        
        this.trimestres = [
          { 
            id: 1, 
            nombre: 'Primer Trimestre', 
            fecha_inicio: `${anoActual}-05-01`, 
            fecha_fin: `${anoActual}-07-31` 
          },
          { 
            id: 2, 
            nombre: 'Segundo Trimestre', 
            fecha_inicio: `${anoActual}-08-01`, 
            fecha_fin: `${anoActual}-10-31` 
          },
          { 
            id: 3, 
            nombre: 'Tercer Trimestre', 
            fecha_inicio: `${anoActual}-11-01`, 
            fecha_fin: `${anoActual + 1}-01-31` 
          }
        ];
      }
    });
  }
  
  cargarEvaluaciones(materiaId: number): void {
    this.evaluacionesLoading = true;
    this.evaluaciones = [];
    
    this.evaluacionesService.getEvaluacionesPorMateria(materiaId).subscribe({
      next: (response: any) => {
        console.log('Evaluaciones originales por materia:', response);
        
        let evaluacionesOriginales: any[] = [];
        
        if (response && response.evaluaciones) {
          evaluacionesOriginales = response.evaluaciones;
        } else {
          evaluacionesOriginales = [];
        }

        // Filtrar solo evaluaciones del año actual
        this.evaluaciones = this.filtrarEvaluacionesAnoActual(evaluacionesOriginales);
        
        console.log(`Evaluaciones filtradas para el año ${this.anoActual}:`, this.evaluaciones);
        
        this.evaluacionesLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar evaluaciones:', error);
        this.evaluacionesLoading = false;
        
        // Fallback a datos simulados del año actual
        this.cargarEvaluacionesSimuladas();
      }
    });
  }
  
  cargarEvaluacionesSimuladas(): void {
    setTimeout(() => {
      const anoActual = new Date().getFullYear();
      const mesActual = String(new Date().getMonth() + 1).padStart(2, '0');
      
      this.evaluaciones = [
        {
          id: 1,
          titulo: 'Examen parcial',
          tipo_evaluacion: { id: 2, nombre: 'EXAMEN', nombre_display: 'Examen' },
          fecha_asignacion: `${anoActual}-${mesActual}-10`,
          fecha_entrega: `${anoActual}-${mesActual}-15`,
          porcentaje_nota_final: 20,
          modelo: 'entregable'
        },
        {
          id: 2,
          titulo: 'Participación semana 1',
          tipo_evaluacion: { id: 3, nombre: 'PARTICIPACION', nombre_display: 'Participación' },
          fecha_registro: `${anoActual}-${mesActual}-05`,
          porcentaje_nota_final: 5,
          modelo: 'participacion'
        }
      ];
      this.evaluacionesLoading = false;
    }, 500);
  }
  
  toggleFormulario(): void {
    this.mostrarFormulario = !this.mostrarFormulario;
    if (this.mostrarFormulario) {
      this.resetearFormulario();
    }
  }
  
  resetearFormulario(): void {
    this.evaluacionForm.reset({
      materia_id: this.materiaSeleccionada,
      tipo_evaluacion_id: null,
      trimestre_id: null,
      titulo: '',
      descripcion: '',
      porcentaje_nota_final: 10,
      publicado: false,
      fecha_asignacion: this.obtenerFechaActual(),
      fecha_entrega: '',
      fecha_limite: '',
      nota_maxima: 100,
      nota_minima_aprobacion: 51,
      permite_entrega_tardia: false,
      penalizacion_tardio: 0,
      fecha_registro: this.obtenerFechaActual(),
      criterios_participacion: '',
      escala_calificacion: 'NUMERICA'
    });
    this.error = '';
    this.mensaje = '';
  }
  
  actualizarValidacionesPorTipo(): void {
    const fechaAsignacionControl = this.evaluacionForm.get('fecha_asignacion');
    const fechaEntregaControl = this.evaluacionForm.get('fecha_entrega');
    const fechaRegistroControl = this.evaluacionForm.get('fecha_registro');
    
    if (this.esEntregable) {
      // Para evaluaciones entregables
      fechaAsignacionControl?.setValidators([Validators.required]);
      fechaEntregaControl?.setValidators([Validators.required]);
      fechaRegistroControl?.clearValidators();
    } else {
      // Para evaluaciones de participación
      fechaAsignacionControl?.clearValidators();
      fechaEntregaControl?.clearValidators();
      fechaRegistroControl?.setValidators([Validators.required]);
    }
    
    fechaAsignacionControl?.updateValueAndValidity();
    fechaEntregaControl?.updateValueAndValidity();
    fechaRegistroControl?.updateValueAndValidity();
  }
  
  crearEvaluacion(): void {
    if (this.evaluacionForm.invalid) {
      this.marcarCamposInvalidos();
      this.error = "Por favor complete todos los campos requeridos";
      return;
    }
    
    const formData = this.prepararDatosEvaluacion();
    
    // Validar datos antes de enviar
    const validacion = this.evaluacionesService.validarDatosEvaluacion(formData);
    
    if (!validacion.valido) {
      this.error = `Por favor corrija los siguientes errores: ${validacion.errores.join(', ')}`;
      return;
    }
    
    this.guardandoEvaluacion = true;
    this.error = '';
    this.mensaje = '';
    
    console.log('Creando evaluación con datos:', JSON.stringify(formData, null, 2));
    
    this.evaluacionesService.createEvaluacion(formData).subscribe({
      next: (response: any) => {
        console.log('Respuesta exitosa al crear evaluación:', response);
        this.mensaje = response.mensaje || 'Evaluación creada con éxito';
        this.guardandoEvaluacion = false;
        
        // Recargar evaluaciones y ocultar formulario
        if (this.materiaSeleccionada) {
          this.cargarEvaluaciones(this.materiaSeleccionada);
        }
        this.mostrarFormulario = false;
      },
      error: (error) => {
        console.error('Error detallado al crear evaluación:', error);
        
        // Mostrar mensaje de error específico si está disponible
        if (error.error && error.error.error) {
          this.error = error.error.error;
        } else if (error.error && error.error.detail) {
          this.error = error.error.detail;
        } else if (error.message) {
          this.error = error.message;
        } else {
          this.error = 'Error al crear la evaluación. Intente nuevamente.';
        }
        
        this.guardandoEvaluacion = false;
      }
    });
  }
  
  prepararDatosEvaluacion(): any {
    const formData = { ...this.evaluacionForm.value };
    
    // Formatear fechas en YYYY-MM-DD
    if (formData.fecha_asignacion) {
      formData.fecha_asignacion = this.evaluacionesService.formatearFechaParaBackend(formData.fecha_asignacion);
    }
    
    if (formData.fecha_entrega) {
      formData.fecha_entrega = this.evaluacionesService.formatearFechaParaBackend(formData.fecha_entrega);
    }
    
    if (formData.fecha_limite) {
      formData.fecha_limite = this.evaluacionesService.formatearFechaParaBackend(formData.fecha_limite);
    }
    
    if (formData.fecha_registro) {
      formData.fecha_registro = this.evaluacionesService.formatearFechaParaBackend(formData.fecha_registro);
    }
    
    // Convertir valores numéricos string a números
    formData.materia_id = Number(formData.materia_id);
    formData.tipo_evaluacion_id = Number(formData.tipo_evaluacion_id);
    formData.trimestre_id = Number(formData.trimestre_id);
    formData.porcentaje_nota_final = Number(formData.porcentaje_nota_final);
    
    if (formData.nota_maxima) {
      formData.nota_maxima = Number(formData.nota_maxima);
    }
    
    if (formData.nota_minima_aprobacion) {
      formData.nota_minima_aprobacion = Number(formData.nota_minima_aprobacion);
    }
    
    if (formData.penalizacion_tardio) {
      formData.penalizacion_tardio = Number(formData.penalizacion_tardio);
    }
    
    // Eliminar campos innecesarios según el tipo
    if (this.esEntregable) {
      delete formData.fecha_registro;
      delete formData.criterios_participacion;
      delete formData.escala_calificacion;
    } else {
      delete formData.fecha_asignacion;
      delete formData.fecha_entrega;
      delete formData.fecha_limite;
      delete formData.nota_maxima;
      delete formData.nota_minima_aprobacion;
      delete formData.permite_entrega_tardia;
      delete formData.penalizacion_tardio;
    }
    
    // Si fecha_limite está vacía, eliminarla
    if (formData.fecha_limite === '') {
      delete formData.fecha_limite;
    }
    
    // Asegurar valores booleanos correctos
    if (formData.publicado === '') {
      formData.publicado = false;
    }
    
    if (formData.permite_entrega_tardia === '') {
      formData.permite_entrega_tardia = false;
    }
    
    // Agregar el modelo explícitamente
    formData.modelo = this.esEntregable ? 'entregable' : 'participacion';
    
    console.log('Datos a enviar para crear evaluación:', formData);
    
    return formData;
  }
  
  marcarCamposInvalidos(): void {
    Object.keys(this.evaluacionForm.controls).forEach(field => {
      const control = this.evaluacionForm.get(field);
      if (control?.invalid) {
        control.markAsTouched({ onlySelf: true });
      }
    });
  }
  
  getMateriaSeleccionada(): Materia | undefined {
    const materiaId = this.evaluacionForm.get('materia_id')?.value;
    return this.materias.find(m => m.id == materiaId);
  }
  
  getTipoEvaluacionSeleccionado(): TipoEvaluacion | undefined {
    const tipoId = this.evaluacionForm.get('tipo_evaluacion_id')?.value;
    return this.tiposEvaluacion.find(t => t.id == tipoId);
  }
  
  getTrimestreSeleccionado(): any | undefined {
    const trimestreId = this.evaluacionForm.get('trimestre_id')?.value;
    return this.trimestres.find(t => t.id == trimestreId);
  }
  
  getEstadoEvaluacion(evaluacion: any): any {
    return this.evaluacionesService.getEstadoEvaluacion(evaluacion);
  }
  
  eliminarEvaluacion(evaluacion: any): void {
    if (!confirm(`¿Está seguro que desea eliminar la evaluación "${evaluacion.titulo}"?`)) {
      return;
    }
    
    this.evaluacionesService.deleteEvaluacion(evaluacion.id).subscribe({
      next: (response: any) => {
        console.log('Respuesta de eliminar evaluación:', response);
        this.mensaje = response.mensaje || 'Evaluación eliminada con éxito';
        
        // Recargar evaluaciones
        if (this.materiaSeleccionada) {
          this.cargarEvaluaciones(this.materiaSeleccionada);
        }
      },
      error: (error) => {
        console.error('Error al eliminar evaluación:', error);
        this.error = error.error?.error || 'Error al eliminar la evaluación. Intente nuevamente.';
      }
    });
  }
  
  formatearFecha(fecha: string): string {
    if (!fecha) return '-';
    
    const fechaObj = new Date(fecha);
    return fechaObj.toLocaleDateString('es-ES');
  }
  
  formatearPorcentaje(valor: number): string {
    return `${valor}%`;
  }
  
  // Método para mostrar el modal de configuración
  mostrarConfiguracionPorcentaje(): void {
    this.configurandoPorcentaje = true;
  }
  
  // Método para guardar la configuración de porcentaje
  guardarConfiguracionPorcentaje(): void {
    if (this.configuracionForm.invalid) {
      Object.keys(this.configuracionForm.controls).forEach(field => {
        const control = this.configuracionForm.get(field);
        if (control?.invalid) {
          control.markAsTouched({ onlySelf: true });
        }
      });
      return;
    }
    
    const formData = { ...this.configuracionForm.value };
    formData.materia_id = Number(formData.materia_id);
    formData.tipo_evaluacion_id = Number(formData.tipo_evaluacion_id);
    formData.porcentaje = Number(formData.porcentaje);
    
    this.evaluacionesService.configurarPorcentajeEvaluacion(formData).subscribe({
      next: (response: any) => {
        console.log('Configuración guardada:', response);
        this.mensaje = 'Configuración de porcentaje guardada correctamente';
        this.configurandoPorcentaje = false;
        this.cargarConfiguracionPorcentajes(this.materiaSeleccionada);
      },
      error: (error) => {
        console.error('Error al guardar configuración:', error);
        this.error = error.error?.mensaje || 'Error al guardar la configuración';
      }
    });
  }
  
  // Método para validar el porcentaje de una evaluación
  validarPorcentajeEvaluacion(): void {
    const materiaId = this.evaluacionForm.get('materia_id')?.value;
    const tipoId = this.evaluacionForm.get('tipo_evaluacion_id')?.value;
    const porcentaje = this.evaluacionForm.get('porcentaje_nota_final')?.value;
    
    if (materiaId && tipoId && porcentaje) {
      // Conversión explícita a number para evitar problemas de tipo
      this.evaluacionesService.verificarPorcentajeDisponible(
        Number(materiaId), 
        Number(tipoId), 
        Number(porcentaje), 
        this.evaluaciones
      ).subscribe({
        next: (resultado) => {
          if (!resultado.disponible) {
            this.error = resultado.mensaje;
          } else {
            this.error = '';
          }
        },
        error: (err) => {
          console.error('Error al verificar porcentaje:', err);
        }
      });
    }
  }
  
  cargarConfiguracionPorcentajes(materiaId: number | null): void {
    // Si materiaId es null, no hacer nada
    if (materiaId === null) {
      this.configuracionPorcentajes = [];
      return;
    }
    
    // Ahora podemos llamar al servicio con seguridad
    this.evaluacionesService.getConfiguracionPorcentajes(materiaId).subscribe({
      next: (response: any) => {
        console.log('Configuración de porcentajes:', response);
        this.configuracionPorcentajes = Array.isArray(response) ? response : [];
      },
      error: (error) => {
        console.error('Error al cargar configuración de porcentajes:', error);
        this.configuracionPorcentajes = [];
      }
    });
  }
  
  calcularPorcentajeRestante(): number {
    const tipoEvaluacionId = this.evaluacionForm.get('tipo_evaluacion_id')?.value;
    
    if (!tipoEvaluacionId || !this.materiaSeleccionada) {
      return 100;
    }
    
    // Convertir explícitamente a número
    const tipoId = Number(tipoEvaluacionId);
    
    // Calcular el porcentaje ya utilizado para este tipo de evaluación
    const porcentajeUsado = this.evaluacionesService.calcularPorcentajeUsado(
      this.evaluaciones, 
      tipoId
    );
    
    // Buscar la configuración personalizada para este tipo
    const configuracion = this.configuracionPorcentajes.find(
      c => c.tipo_evaluacion_id == tipoId
    );
    
    // Obtener el porcentaje máximo permitido (personalizado o por defecto 100)
    const porcentajeMaximo = configuracion ? Number(configuracion.porcentaje) : 100;
    
    // Calcular el restante
    return Math.max(0, porcentajeMaximo - porcentajeUsado);
  }
}
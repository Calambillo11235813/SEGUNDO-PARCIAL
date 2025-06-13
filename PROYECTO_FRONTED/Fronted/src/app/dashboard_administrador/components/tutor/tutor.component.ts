import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { UsuariosService } from '../../../services/usuarios.service';
import { TutorService } from '../../../services/tutor.service';
import { EstudiantesService } from '../../../services/estudiantes.service';

@Component({
  selector: 'app-tutor',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './tutor.component.html'
})
export class TutorComponent implements OnInit {
  tutorForm: FormGroup;
  tutores: any[] = [];
  tutoresFiltrados: any[] = [];
  estudiantes: any[] = [];
  estudiantesDisponibles: any[] = [];
  estudiantesAsignados: any[] = [];
  
  loading = false;
  mensaje = '';
  error = '';
  modoEdicion = false;
  tutorId: number | null = null;
  mostrarPassword = false;
  mostrarModalAsignacion = false;
  tutorSeleccionado: any = null;
  
  // Agregar estas propiedades
  tutorDetalle: any = null;
  mostrandoDetalle = false;

  constructor(
    private fb: FormBuilder,
    private usuariosService: UsuariosService,
    private tutorService: TutorService,
    private estudiantesService: EstudiantesService
  ) {
    // Inicializar arrays vacíos para evitar errores
    this.tutores = [];
    this.tutoresFiltrados = [];
    this.estudiantes = [];
    this.estudiantesDisponibles = [];
    this.estudiantesAsignados = [];
    
    this.tutorForm = this.fb.group({
      nombre: ['', [Validators.required]],
      apellido: ['', [Validators.required]],
      codigo: ['', [Validators.required]],
      telefono: ['', [Validators.required, Validators.pattern('[0-9]{8}')]],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }
  
  ngOnInit(): void {
    this.cargarTutoresConDetalle(); // Cambiar por este método
    this.cargarEstudiantes();
  }
  
  cargarTutores(): void {
    this.loading = true;
    this.usuariosService.getUsuariosPorRol('Tutor').subscribe({
      next: (data: any[]) => {
        this.tutores = data;
        this.tutoresFiltrados = [...data];
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Error al cargar tutores';
        this.loading = false;
      }
    });
  }

  cargarEstudiantes(): void {
    this.estudiantesService.getEstudiantes().subscribe({
      next: (data: any) => {
        // Asegurar que sea un array
        this.estudiantes = Array.isArray(data) ? data : [];
        console.log('Estudiantes cargados:', this.estudiantes.length);
      },
      error: (err: any) => {
        console.error('Error al cargar estudiantes:', err);
        this.estudiantes = []; // Inicializar como array vacío en caso de error
        this.error = 'Error al cargar estudiantes';
      }
    });
  }
  
  guardarTutor(): void {
    if (this.tutorForm.invalid) {
      Object.keys(this.tutorForm.controls).forEach(key => {
        this.tutorForm.get(key)?.markAsTouched();
      });
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    if (this.modoEdicion && this.tutorId) {
      // Actualizar tutor existente
      const tutorData = {
        nombre: this.tutorForm.value.nombre,
        apellido: this.tutorForm.value.apellido,
        codigo: this.tutorForm.value.codigo,
        telefono: this.tutorForm.value.telefono
      };
      
      this.usuariosService.actualizarUsuario(this.tutorId, tutorData).subscribe({
        next: (response: any) => {
          this.mensaje = response.mensaje || 'Tutor actualizado con éxito';
          this.cancelarEdicion();
          this.cargarTutoresConDetalle(); // Usar el método mejorado
        },
        error: (err: any) => {
          this.error = err.error?.error || 'Error al actualizar tutor';
          this.loading = false;
        }
      });
    } else {
      // Crear nuevo tutor
      const tutorData = {
        ...this.tutorForm.value,
        rol_id: 4 // ID del rol tutor
      };
      
      this.usuariosService.crearUsuario(tutorData).subscribe({
        next: (response: any) => {
          this.mensaje = response.mensaje || 'Tutor creado con éxito';
          this.tutorForm.reset();
          this.loading = false;
          this.cargarTutoresConDetalle(); // Usar el método mejorado
        },
        error: (err: any) => {
          this.error = err.error?.error || 'Error al crear tutor';
          this.loading = false;
        }
      });
    }
  }
  
  editarTutor(tutor: any): void {
    this.modoEdicion = true;
    this.tutorId = tutor.id;
    
    this.tutorForm.patchValue({
      nombre: tutor.nombre,
      apellido: tutor.apellido,
      codigo: tutor.codigo,
      telefono: tutor.telefono
    });
    
    // Quitar validador de contraseña para edición
    this.tutorForm.get('password')?.clearValidators();
    this.tutorForm.get('password')?.updateValueAndValidity();
  }
  
  eliminarTutor(id: number): void {
    if (confirm('¿Está seguro de que desea eliminar este tutor?')) {
      this.usuariosService.eliminarUsuario(id).subscribe({
        next: () => {
          this.mensaje = 'Tutor eliminado con éxito';
          this.cargarTutoresConDetalle(); // Usar el método mejorado
        },
        error: (err: any) => {
          this.error = 'Error al eliminar tutor';
        }
      });
    }
  }
  
  cancelarEdicion(): void {
    this.modoEdicion = false;
    this.tutorId = null;
    this.tutorForm.reset();
    
    // Restaurar validador de contraseña
    this.tutorForm.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
    this.tutorForm.get('password')?.updateValueAndValidity();
  }
  
  filtrarTutores(termino: string): void {
    if (!termino) {
      this.tutoresFiltrados = [...this.tutores];
      return;
    }
    
    termino = termino.toLowerCase();
    this.tutoresFiltrados = this.tutores.filter(
      tutor => tutor.codigo.toLowerCase().includes(termino) || 
               tutor.nombre.toLowerCase().includes(termino) || 
               tutor.apellido.toLowerCase().includes(termino)
    );
  }

  // Métodos para asignación de estudiantes
  abrirModalAsignacion(tutor: any): void {
    this.tutorSeleccionado = tutor;
    this.mostrarModalAsignacion = true;
    this.cargarEstudiantesAsignacion();
  }

  cargarEstudiantesAsignacion(): void {
    if (!this.tutorSeleccionado) return;

    // Cargar estudiantes asignados al tutor
    this.tutorService.getEstudiantesTutor(this.tutorSeleccionado.id).subscribe({
      next: (estudiantesAsignados: any[]) => {
        this.estudiantesAsignados = Array.isArray(estudiantesAsignados) ? estudiantesAsignados : [];
        
        // Asegurar que this.estudiantes sea un array antes de filtrar
        const todosLosEstudiantes = Array.isArray(this.estudiantes) ? this.estudiantes : [];
        
        // Filtrar estudiantes disponibles (no asignados)
        const idsAsignados = this.estudiantesAsignados.map(est => est.id);
        this.estudiantesDisponibles = todosLosEstudiantes.filter(
          est => !idsAsignados.includes(est.id)
        );
      },
      error: (err: any) => {
        console.error('Error al cargar estudiantes del tutor:', err);
        // Si hay error, mostrar todos los estudiantes como disponibles
        const todosLosEstudiantes = Array.isArray(this.estudiantes) ? this.estudiantes : [];
        this.estudiantesDisponibles = [...todosLosEstudiantes];
        this.estudiantesAsignados = [];
      }
    });
  }

  asignarEstudiante(estudiante: any): void {
    if (!this.tutorSeleccionado || !estudiante?.id) return;

    this.tutorService.asignarEstudiantesTutor(this.tutorSeleccionado.id, [estudiante.id]).subscribe({
      next: (response) => {
        this.mensaje = `Estudiante ${estudiante.nombre} ${estudiante.apellido} asignado correctamente`;
        this.cargarEstudiantesAsignacion(); // Recargar listas
        this.error = ''; // Limpiar errores previos
      },
      error: (err: any) => {
        console.error('Error al asignar estudiante:', err);
        this.error = err.error?.mensaje || 'Error al asignar estudiante';
        this.mensaje = ''; // Limpiar mensajes previos
      }
    });
  }

  desasignarEstudiante(estudiante: any): void {
    if (!this.tutorSeleccionado || !estudiante?.id) return;

    if (confirm(`¿Está seguro de desasignar a ${estudiante.nombre} ${estudiante.apellido}?`)) {
      this.tutorService.desasignarEstudiantesTutor(this.tutorSeleccionado.id, [estudiante.id]).subscribe({
        next: (response) => {
          this.mensaje = `Estudiante ${estudiante.nombre} ${estudiante.apellido} desasignado correctamente`;
          this.cargarEstudiantesAsignacion(); // Recargar listas
          this.error = ''; // Limpiar errores previos
        },
        error: (err: any) => {
          console.error('Error al desasignar estudiante:', err);
          this.error = err.error?.mensaje || 'Error al desasignar estudiante';
          this.mensaje = ''; // Limpiar mensajes previos
        }
      });
    }
  }

  asignarMultiplesEstudiantes(): void {
    const checkboxes = document.querySelectorAll('input[name="estudiantesSeleccionados"]:checked') as NodeListOf<HTMLInputElement>;
    const estudiantesIds = Array.from(checkboxes).map(cb => parseInt(cb.value));

    if (estudiantesIds.length === 0) {
      this.error = 'Seleccione al menos un estudiante';
      return;
    }

    this.tutorService.asignarEstudiantesTutor(this.tutorSeleccionado.id, estudiantesIds).subscribe({
      next: () => {
        this.mensaje = `${estudiantesIds.length} estudiante(s) asignado(s) correctamente`;
        this.cargarEstudiantesAsignacion();
        // Limpiar checkboxes
        checkboxes.forEach(cb => cb.checked = false);
      },
      error: (err: any) => {
        this.error = 'Error al asignar estudiantes';
      }
    });
  }

  cerrarModalAsignacion(): void {
    this.mostrarModalAsignacion = false;
    this.tutorSeleccionado = null;
    this.estudiantesDisponibles = [];
    this.estudiantesAsignados = [];
  }

  toggleMostrarPassword(): void {
    this.mostrarPassword = !this.mostrarPassword;
  }

  // Agregar estos métodos al componente existente:

  reiniciarFormulario(): void {
    this.modoEdicion = false;
    this.tutorForm.reset();
    this.tutorId = null;
    this.mensaje = '';
    this.error = '';
  }

  toggleSelectAll(event: any): void {
    const checkboxes = document.querySelectorAll('input[name="estudiantesSeleccionados"]') as NodeListOf<HTMLInputElement>;
    checkboxes.forEach(cb => cb.checked = event.target.checked);
  }

  trackByEstudianteId(index: number, estudiante: any): number {
    return estudiante.id;
  }

  // Método para obtener información específica de un tutor
  obtenerTutorDetalle(tutorId: number): void {
    this.loading = true;
    this.tutorService.getTutor(tutorId).subscribe({
      next: (tutor: any) => {
        this.tutorDetalle = tutor;
        this.mostrandoDetalle = true;
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Error al cargar detalles del tutor';
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  // Método mejorado para cargar tutores con más información
  cargarTutoresConDetalle(): void {
    this.loading = true;
    this.usuariosService.getUsuariosPorRol('Tutor').subscribe({
      next: (tutores: any[]) => {
        // Para cada tutor, obtener información adicional
        const promises = tutores.map(tutor => 
          this.tutorService.getEstudiantesTutor(tutor.id).toPromise().then(estudiantes => ({
            ...tutor,
            totalEstudiantes: estudiantes?.length || 0,
            estudiantes: estudiantes || []
          })).catch(() => ({
            ...tutor,
            totalEstudiantes: 0,
            estudiantes: []
          }))
        );

        Promise.all(promises).then(tutoresConDetalle => {
          this.tutores = tutoresConDetalle;
          this.tutoresFiltrados = [...tutoresConDetalle];
          this.loading = false;
        });
      },
      error: (err: any) => {
        this.error = 'Error al cargar tutores';
        this.loading = false;
        console.error('Error:', err);
      }
    });
  }

  // Método para ver detalles completos del tutor
  verDetallesTutor(tutor: any): void {
    this.obtenerTutorDetalle(tutor.id);
  }

  // Método para cerrar el modal de detalles
  cerrarDetallesTutor(): void {
    this.mostrandoDetalle = false;
    this.tutorDetalle = null;
  }
}
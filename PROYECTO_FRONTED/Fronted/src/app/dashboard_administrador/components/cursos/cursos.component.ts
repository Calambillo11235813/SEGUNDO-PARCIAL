import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CursosService } from '../../../services/cursos.service';
import { NivelesService } from '../../../services/niveles.service';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-cursos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cursos.component.html'
})
export class CursosComponent implements OnInit {
  // Variables para gestionar el formulario
  cursoForm: FormGroup;
  estudianteForm: FormGroup;
  modoEdicion = false;
  idCursoEditando: number | null = null;
  loading = false;
  mensaje = '';
  error = '';

  // Variables para la data
  cursos: any[] = [];
  cursosFiltrados: any[] = [];
  niveles: any[] = [];
  estudiantes: any[] = [];
  estudiantesSinCurso: any[] = []; // ✅ Esta variable ahora se usará correctamente

  // Variables para modal de asignación
  mostrarModalAsignacion = false;
  cursoSeleccionado: any = null;
  estudiantesDelCurso: any[] = [];
  cargandoEstudiantes = false;
  asignandoEstudiante = false;

  constructor(
    private fb: FormBuilder,
    private cursosService: CursosService,
    private nivelesService: NivelesService,
    private usuariosService: UsuariosService,
    private router: Router
  ) {
    this.cursoForm = this.fb.group({
      nivel: [null, Validators.required],
      grado: [null, [Validators.required, Validators.min(1)]],
      paralelo: ['', [Validators.required, Validators.maxLength(1)]]
    });

    this.estudianteForm = this.fb.group({
      estudiante: [null, Validators.required]
    });
  }

  ngOnInit(): void {
    this.cargarNiveles();
    this.cargarCursos();
    this.cargarEstudiantes();
  }

  // Cargar datos iniciales
  cargarNiveles(): void {
    this.loading = true;
    this.nivelesService.getNiveles().subscribe({
      next: (data) => {
        this.niveles = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar niveles:', error);
        this.error = 'Error al cargar niveles';
        this.loading = false;
      }
    });
  }

  cargarCursos(): void {
    this.loading = true;
    this.cursosService.getCursos().subscribe({
      next: (data) => {
        this.cursos = data;
        this.cursosFiltrados = [...this.cursos];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar cursos:', error);
        this.error = 'Error al cargar cursos';
        this.loading = false;
      }
    });
  }

  // ✅ ACTUALIZAR: Cargar estudiantes sin curso específicamente
  cargarEstudiantesSinCurso(): void {
    this.cursosService.getEstudiantesSinCurso().subscribe({
      next: (response) => {
        this.estudiantesSinCurso = response.estudiantes || [];
        console.log(`Estudiantes sin curso cargados: ${this.estudiantesSinCurso.length}`);
      },
      error: (error) => {
        console.error('Error al cargar estudiantes sin curso:', error);
        this.estudiantesSinCurso = [];
      }
    });
  }

  // ✅ MANTENER: Cargar todos los estudiantes para referencia
  cargarEstudiantes(): void {
    this.usuariosService.getUsuariosPorRol('Estudiante').subscribe({
      next: (data) => {
        this.estudiantes = data;
        // También cargar estudiantes sin curso
        this.cargarEstudiantesSinCurso();
      },
      error: (error) => {
        console.error('Error al cargar estudiantes:', error);
      }
    });
  }

  // ✅ ACTUALIZAR: Modal de asignación
  abrirModalAsignacion(curso: any): void {
    this.cursoSeleccionado = curso;
    this.mostrarModalAsignacion = true;
    this.estudianteForm.reset();
    this.mensaje = '';
    this.error = '';
    
    // Cargar datos del modal
    this.cargarEstudiantesDelCurso();
    this.cargarEstudiantesSinCurso(); // ✅ Cargar estudiantes disponibles
  }

  cerrarModalAsignacion(): void {
    this.mostrarModalAsignacion = false;
    this.cursoSeleccionado = null;
    this.estudiantesDelCurso = [];
    this.estudianteForm.reset();
    this.mensaje = '';
    this.error = '';
  }

  cargarEstudiantesDelCurso(): void {
    if (!this.cursoSeleccionado) return;

    this.cargandoEstudiantes = true;
    
    // ✅ USAR ENDPOINT REAL
    this.cursosService.getEstudiantesDeCurso(this.cursoSeleccionado.id).subscribe({
      next: (response) => {
        this.estudiantesDelCurso = response.estudiantes || [];
        this.cargandoEstudiantes = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes del curso:', error);
        this.estudiantesDelCurso = [];
        this.cargandoEstudiantes = false;
      }
    });
  }

  asignarEstudianteACurso(): void {
    if (this.estudianteForm.invalid || !this.cursoSeleccionado) {
      return;
    }

    this.asignandoEstudiante = true;
    this.mensaje = '';
    this.error = '';

    const estudianteId = this.estudianteForm.value.estudiante;
    const cursoId = this.cursoSeleccionado.id;

    this.cursosService.asignarEstudianteACurso(estudianteId, cursoId).subscribe({
      next: (response) => {
        this.mensaje = `✅ ${response.mensaje}`;
        
        // Actualizar todas las listas
        this.cargarEstudiantes(); // Esto también actualiza estudiantesSinCurso
        this.cargarEstudiantesDelCurso();
        this.estudianteForm.reset();
        this.asignandoEstudiante = false;

        // Auto-cerrar modal después de 2.5 segundos
        setTimeout(() => {
          this.cerrarModalAsignacion();
        }, 2500);
      },
      error: (error) => {
        // ✅ MEJORADO: Manejo específico de errores
        if (error.status === 400 && error.error?.curso_actual) {
          this.error = `❌ ${error.error.error}`;
        } else {
          this.error = error.error?.error || 'Error al asignar estudiante al curso';
        }
        
        console.error('Error al asignar estudiante:', error);
        this.asignandoEstudiante = false;
      }
    });
  }

  desasignarEstudianteDeCurso(estudiante: any): void {
    const confirmMessage = `¿Está seguro de desasignar a ${estudiante.nombre} ${estudiante.apellido} del curso ${this.cursoSeleccionado?.grado}° ${this.cursoSeleccionado?.paralelo}?`;
    
    if (!confirm(confirmMessage)) {
      return;
    }

    this.cursosService.desasignarEstudianteDeCurso(estudiante.id).subscribe({
      next: (response) => {
        this.mensaje = `✅ ${response.mensaje}`;
        
        // Actualizar todas las listas
        this.cargarEstudiantes(); // Esto también actualiza estudiantesSinCurso
        this.cargarEstudiantesDelCurso();
        
        // Limpiar mensaje después de 3 segundos
        setTimeout(() => {
          this.mensaje = '';
        }, 3000);
      },
      error: (error) => {
        this.error = error.error?.error || 'Error al desasignar estudiante del curso';
        console.error('Error al desasignar estudiante:', error);
        
        setTimeout(() => {
          this.error = '';
        }, 3000);
      }
    });
  }

  // Acciones del CRUD existentes
  guardarCurso(): void {
    if (this.cursoForm.invalid) {
      this.cursoForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.mensaje = '';
    this.error = '';

    const cursoData = this.cursoForm.value;

    if (this.modoEdicion && this.idCursoEditando) {
      this.cursosService.updateCurso(this.idCursoEditando, cursoData).subscribe({
        next: (response) => {
          this.mensaje = 'Curso actualizado correctamente';
          this.cargarCursos();
          this.resetForm();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al actualizar el curso';
          console.error('Error al actualizar curso:', error);
          this.loading = false;
        }
      });
    } else {
      this.cursosService.createCurso(cursoData).subscribe({
        next: (response) => {
          this.mensaje = 'Curso creado correctamente';
          this.cargarCursos();
          this.resetForm();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al crear el curso';
          console.error('Error al crear curso:', error);
          this.loading = false;
        }
      });
    }
  }

  editarCurso(curso: any): void {
    this.modoEdicion = true;
    this.idCursoEditando = curso.id;
    
    this.cursoForm.patchValue({
      nivel: curso.nivel,
      grado: curso.grado,
      paralelo: curso.paralelo
    });
    
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  eliminarCurso(id: number): void {
    if (confirm('¿Está seguro de eliminar este curso? Esta acción también eliminará todas las materias asociadas a este curso.')) {
      this.loading = true;
      this.cursosService.deleteCurso(id).subscribe({
        next: (response) => {
          this.mensaje = 'Curso eliminado correctamente';
          this.cargarCursos();
          if (this.idCursoEditando === id) {
            this.resetForm();
          }
        },
        error: (error) => {
          this.error = 'Error al eliminar el curso';
          console.error('Error al eliminar curso:', error);
          this.loading = false;
        }
      });
    }
  }

  verMaterias(cursoId: number): void {
    this.router.navigate(['/admin/materias'], { queryParams: { curso: cursoId } });
  }

  // Utilidades
  resetForm(): void {
    this.cursoForm.reset();
    this.modoEdicion = false;
    this.idCursoEditando = null;
    this.mensaje = '';
    this.error = '';
    this.loading = false;
  }

  cancelarEdicion(): void {
    this.resetForm();
  }

  filtrarCursos(texto: string): void {
    if (!texto) {
      this.cursosFiltrados = [...this.cursos];
      return;
    }
    
    texto = texto.toLowerCase();
    this.cursosFiltrados = this.cursos.filter(curso => {
      const nivelNombre = this.getNombreNivel(curso.nivel).toLowerCase();
      
      return (
        curso.id.toString().includes(texto) ||
        nivelNombre.includes(texto) ||
        curso.grado.toString().includes(texto) ||
        curso.paralelo.toLowerCase().includes(texto)
      );
    });
  }

  getNombreNivel(nivelId: number): string {
    const nivel = this.niveles.find(n => n.id === nivelId);
    return nivel ? nivel.nombre : 'Nivel no encontrado';
  }

  // Métodos auxiliares para el modal
  getEstudianteNombre(estudianteId: number): string {
    const estudiante = this.estudiantes.find(e => e.id === estudianteId);
    return estudiante ? `${estudiante.nombre} ${estudiante.apellido}` : 'Estudiante no encontrado';
  }

  // ✅ ACTUALIZAR: Método para obtener estudiantes disponibles
  getEstudiantesSinCursoActualizados(): any[] {
    return this.estudiantesSinCurso; // ✅ Usar la lista específica
  }

  // ✅ NUEVO: Método para obtener información del estudiante
  getEstudianteInfo(estudianteId: number): any {
    return this.estudiantes.find(e => e.id === estudianteId) || null;
  }
}
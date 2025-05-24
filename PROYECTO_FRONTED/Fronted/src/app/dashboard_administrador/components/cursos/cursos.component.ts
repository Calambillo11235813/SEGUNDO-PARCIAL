import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { CursosService } from '../../../services/cursos.service';
import { NivelesService } from '../../../services/niveles.service';

@Component({
  selector: 'app-cursos',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './cursos.component.html'
})
export class CursosComponent implements OnInit {
  // Variables para gestionar el formulario
  cursoForm: FormGroup;
  modoEdicion = false;
  idCursoEditando: number | null = null;
  loading = false;
  mensaje = '';
  error = '';

  // Variables para la data
  cursos: any[] = [];
  cursosFiltrados: any[] = [];
  niveles: any[] = [];

  constructor(
    private fb: FormBuilder,
    private cursosService: CursosService,
    private nivelesService: NivelesService,
    private router: Router
  ) {
    this.cursoForm = this.fb.group({
      nivel: [null, Validators.required],
      grado: [null, [Validators.required, Validators.min(1)]],
      paralelo: ['', [Validators.required, Validators.maxLength(1)]]
    });
  }

  ngOnInit(): void {
    this.cargarNiveles();
    this.cargarCursos();
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

  // Acciones del CRUD
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
    
    // Desplazarse al formulario
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  eliminarCurso(id: number): void {
    if (confirm('¿Está seguro de eliminar este curso? Esta acción también eliminará todas las materias asociadas a este curso.')) {
      this.loading = true;
      this.cursosService.deleteCurso(id).subscribe({
        next: (response) => {
          this.mensaje = 'Curso eliminado correctamente';
          this.cargarCursos();
          // Si estamos editando el curso que acabamos de eliminar, resetear el formulario
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

  // Navegación a materias del curso
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
      // Buscar el nombre del nivel
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
}
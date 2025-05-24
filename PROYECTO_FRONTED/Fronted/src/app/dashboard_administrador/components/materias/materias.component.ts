import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MateriasService } from '../../../services/materias.service';
import { CursosService } from '../../../services/cursos.service';

@Component({
  selector: 'app-materias',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './materias.component.html'
})
export class MateriasComponent implements OnInit {
  // Variables para gestionar el formulario
  materiaForm: FormGroup;
  modoEdicion = false;
  idMateriaEditando: number | null = null;
  loading = false;
  mensaje = '';
  error = '';

  // Variables para la data
  materias: any[] = [];
  materiasFiltradas: any[] = [];
  cursos: any[] = [];

  constructor(
    private fb: FormBuilder,
    private materiasService: MateriasService,
    private cursosService: CursosService,
    private router: Router
  ) {
    this.materiaForm = this.fb.group({
      curso: [null, Validators.required],
      nombre: ['', [Validators.required, Validators.maxLength(100)]]
    });
  }

  ngOnInit(): void {
    this.cargarCursos();
    this.cargarMaterias();
  }

  // Cargar datos iniciales
  cargarCursos(): void {
    this.loading = true;
    this.cursosService.getCursos().subscribe({
      next: (data) => {
        // Asumimos que los datos del curso ya incluyen la información del nivel
        // Si no es así, necesitaríamos hacer una consulta adicional para obtener los niveles
        this.cursos = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar cursos:', error);
        this.error = 'Error al cargar cursos';
        this.loading = false;
      }
    });
  }

  cargarMaterias(): void {
    this.loading = true;
    this.materiasService.getMaterias().subscribe({
      next: (data) => {
        this.materias = data;
        this.materiasFiltradas = [...this.materias];
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar materias:', error);
        this.error = 'Error al cargar materias';
        this.loading = false;
      }
    });
  }

  // Acciones del CRUD
  guardarMateria(): void {
    if (this.materiaForm.invalid) {
      this.materiaForm.markAllAsTouched();
      return;
    }

    this.loading = true;
    this.mensaje = '';
    this.error = '';

    const materiaData = this.materiaForm.value;

    if (this.modoEdicion && this.idMateriaEditando) {
      this.materiasService.updateMateria(this.idMateriaEditando, materiaData).subscribe({
        next: (response) => {
          this.mensaje = 'Materia actualizada correctamente';
          this.cargarMaterias();
          this.resetForm();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al actualizar la materia';
          console.error('Error al actualizar materia:', error);
          this.loading = false;
        }
      });
    } else {
      this.materiasService.createMateria(materiaData).subscribe({
        next: (response) => {
          this.mensaje = response.mensaje || 'Materia creada correctamente';
          this.cargarMaterias();
          this.resetForm();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al crear la materia';
          console.error('Error al crear materia:', error);
          this.loading = false;
        }
      });
    }
  }

  editarMateria(materia: any): void {
    this.modoEdicion = true;
    this.idMateriaEditando = materia.id;

    this.materiaForm.patchValue({
      curso: materia.curso,
      nombre: materia.nombre
    });

    // Desplazarse al formulario
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  eliminarMateria(id: number): void {
    if (confirm('¿Está seguro de eliminar esta materia?')) {
      this.loading = true;
      this.materiasService.deleteMateria(id).subscribe({
        next: (response) => {
          this.mensaje = response.mensaje || 'Materia eliminada correctamente';
          this.cargarMaterias();
          // Si estamos editando la materia que acabamos de eliminar, resetear el formulario
          if (this.idMateriaEditando === id) {
            this.resetForm();
          }
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al eliminar la materia';
          console.error('Error al eliminar materia:', error);
          this.loading = false;
        }
      });
    }
  }

  // Utilidades
  resetForm(): void {
    this.materiaForm.reset();
    this.modoEdicion = false;
    this.idMateriaEditando = null;
    this.mensaje = '';
    this.error = '';
    this.loading = false;
  }

  cancelarEdicion(): void {
    this.resetForm();
  }

  filtrarMaterias(texto: string): void {
    if (!texto) {
      this.materiasFiltradas = [...this.materias];
      return;
    }

    texto = texto.toLowerCase();
    this.materiasFiltradas = this.materias.filter(materia => {
      const cursoNombre = this.getNombreCurso(materia.curso).toLowerCase();
      return (
        materia.id.toString().includes(texto) ||
        materia.nombre.toLowerCase().includes(texto) ||
        cursoNombre.includes(texto)
      );
    });
  }

  getNombreCurso(cursoId: number): string {
    const curso = this.cursos.find(c => c.id === cursoId);
    if (!curso) return 'Curso no encontrado';
    
    // Incluye el nivel si está disponible
    const nivelInfo = curso.nivel_nombre ? `${curso.nivel_nombre} - ` : '';
    return `${nivelInfo}${curso.grado}° ${curso.paralelo}`;
  }
}
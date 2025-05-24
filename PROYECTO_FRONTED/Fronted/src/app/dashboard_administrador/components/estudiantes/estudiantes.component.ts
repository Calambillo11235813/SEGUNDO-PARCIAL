import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-estudiantes',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './estudiantes.component.html'
})
export class EstudiantesComponent implements OnInit {
  estudianteForm: FormGroup;
  estudiantes: any[] = [];
  estudiantesFiltrados: any[] = [];
  loading = false;
  mensaje = '';
  error = '';
  modoEdicion = false;
  estudianteId: number | null = null;
  mostrarPassword = false;
  
  constructor(
    private fb: FormBuilder,
    private usuariosService: UsuariosService
  ) {
    this.estudianteForm = this.fb.group({
      nombre: ['', [Validators.required]],
      apellido: ['', [Validators.required]],
      codigo: ['', [Validators.required]],
      telefono: [''],
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }
  
  ngOnInit(): void {
    this.cargarEstudiantes();
  }
  
  cargarEstudiantes(): void {
    this.loading = true;
    this.usuariosService.getUsuariosPorRol('Estudiante').subscribe({
      next: (data: any[]) => {
        this.estudiantes = data;
        this.estudiantesFiltrados = [...data];
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Error al cargar estudiantes';
        this.loading = false;
      }
    });
  }
  
  guardarEstudiante(): void {
    if (this.estudianteForm.invalid) {
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    if (this.modoEdicion && this.estudianteId) {
      // Actualizar estudiante existente
      const estudianteData = {
        nombre: this.estudianteForm.value.nombre,
        apellido: this.estudianteForm.value.apellido,
        codigo: this.estudianteForm.value.codigo,
        telefono: this.estudianteForm.value.telefono
      };
      
      this.usuariosService.actualizarUsuario(this.estudianteId, estudianteData).subscribe({
        next: (response: any) => {
          this.mensaje = response.mensaje || 'Estudiante actualizado con éxito';
          this.cancelarEdicion();
          this.cargarEstudiantes();
        },
        error: (err: any) => {
          this.error = err.error?.error || 'Error al actualizar estudiante';
          this.loading = false;
        }
      });
    } else {
      // Crear nuevo estudiante
      const estudianteData = {
        ...this.estudianteForm.value,
        rol_id: 2 // ID del rol estudiante
      };
      
      this.usuariosService.crearUsuario(estudianteData).subscribe({
        next: (response: any) => {
          this.mensaje = response.mensaje || 'Estudiante creado con éxito';
          this.estudianteForm.reset();
          this.loading = false;
          this.cargarEstudiantes();
        },
        error: (err: any) => {
          this.error = err.error?.error || 'Error al crear estudiante';
          this.loading = false;
        }
      });
    }
  }
  
  editarEstudiante(estudiante: any): void {
    this.modoEdicion = true;
    this.estudianteId = estudiante.id;
    
    this.estudianteForm.patchValue({
      nombre: estudiante.nombre,
      apellido: estudiante.apellido,
      codigo: estudiante.codigo,
      telefono: estudiante.telefono
    });
    
    // Quitar validador de contraseña para edición
    this.estudianteForm.get('password')?.clearValidators();
    this.estudianteForm.get('password')?.updateValueAndValidity();
  }
  
  eliminarEstudiante(id: number): void {
    if (confirm('¿Está seguro de eliminar este estudiante?')) {
      this.loading = true;
      this.usuariosService.eliminarUsuario(id).subscribe({
        next: () => {
          this.mensaje = 'Estudiante eliminado con éxito';
          this.loading = false;
          this.cargarEstudiantes();
        },
        error: (err: any) => {
          this.error = err.error?.error || 'Error al eliminar estudiante';
          this.loading = false;
        }
      });
    }
  }
  
  cancelarEdicion(): void {
    this.modoEdicion = false;
    this.estudianteId = null;
    this.estudianteForm.reset();
    
    // Restaurar validador de contraseña
    this.estudianteForm.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
    this.estudianteForm.get('password')?.updateValueAndValidity();
  }
  
  filtrarEstudiantes(termino: string): void {
    if (!termino) {
      this.estudiantesFiltrados = [...this.estudiantes];
      return;
    }
    
    termino = termino.toLowerCase();
    this.estudiantesFiltrados = this.estudiantes.filter(
      est => est.codigo.toLowerCase().includes(termino) || 
             est.nombre.toLowerCase().includes(termino) || 
             est.apellido.toLowerCase().includes(termino)
    );
  }
}
import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-profesores',
  templateUrl: './profesores.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class ProfesoresComponent implements OnInit {
  profesores: any[] = [];
  profesoresFiltrados: any[] = []; // Para búsqueda y filtrado
  profesorForm: FormGroup;
  mostrarModal = false;
  modoEdicion = false;
  profesorIdActual: number | null = null;
  mostrarPassword = false;
  mensaje = '';
  error = '';
  cargando = false;

  constructor(
    private usuariosService: UsuariosService,
    private fb: FormBuilder
  ) {
    this.profesorForm = this.fb.group({
      codigo: ['', Validators.required],
      nombre: ['', Validators.required],
      apellido: ['', Validators.required],
      telefono: ['', [Validators.required, Validators.pattern('[0-9]{8}')]], // Validación para teléfono
      password: ['', [Validators.required, Validators.minLength(6)]]
    });
  }

  ngOnInit(): void {
    this.cargarProfesores();
  }

  cargarProfesores(): void {
    this.cargando = true;
    this.usuariosService.getUsuariosPorRol('Profesor').subscribe({
      next: (data) => {
        this.profesores = data;
        this.profesoresFiltrados = [...data];
        this.cargando = false;
      },
      error: (error) => {
        console.error('Error al cargar profesores:', error);
        this.error = 'Error al cargar los profesores';
        this.cargando = false;
      }
    });
  }

  // Método para filtrar profesores
  filtrarProfesores(termino: string): void {
    if (!termino) {
      this.profesoresFiltrados = [...this.profesores];
      return;
    }
    
    termino = termino.toLowerCase();
    this.profesoresFiltrados = this.profesores.filter(profesor => 
      profesor.codigo?.toLowerCase().includes(termino) ||
      profesor.nombre?.toLowerCase().includes(termino) ||
      profesor.apellido?.toLowerCase().includes(termino) ||
      profesor.telefono?.toString().includes(termino)
    );
  }

  abrirModalCrear(): void {
    this.modoEdicion = false;
    this.profesorIdActual = null;
    this.profesorForm.reset();
    
    // Reactivar validación de contraseña para nuevo profesor
    this.profesorForm.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
    this.profesorForm.get('password')?.updateValueAndValidity();
    
    this.mostrarModal = true;
  }

  editarProfesor(profesor: any): void {
    this.modoEdicion = true;
    this.profesorIdActual = profesor.id;
    this.profesorForm.patchValue({
      codigo: profesor.codigo,
      nombre: profesor.nombre,
      apellido: profesor.apellido,
      telefono: profesor.telefono
    });
    
    // Desactivar validación de contraseña al editar
    this.profesorForm.get('password')?.clearValidators();
    this.profesorForm.get('password')?.updateValueAndValidity();
    
    this.mostrarModal = true;
  }

  cerrarModal(): void {
    this.mostrarModal = false;
    setTimeout(() => {
      this.profesorForm.reset();
    }, 300); // Esperar a que termine la animación
  }

  cancelarEdicion(): void {
    this.modoEdicion = false;
    this.profesorIdActual = null;
    this.profesorForm.reset();

    // Reactivar validación de contraseña para nuevo profesor
    this.profesorForm.get('password')?.setValidators([Validators.required, Validators.minLength(6)]);
    this.profesorForm.get('password')?.updateValueAndValidity();
  }

  guardarProfesor(): void {
    if (this.profesorForm.invalid) {
      // Marcar todos los campos como tocados para mostrar validaciones
      Object.keys(this.profesorForm.controls).forEach(key => {
        this.profesorForm.get(key)?.markAsTouched();
      });
      return;
    }

    this.cargando = true;
    this.mensaje = '';
    this.error = '';

    if (this.modoEdicion && this.profesorIdActual !== null) {
      // Lógica para actualizar profesor existente
      const profesorData = {
        ...this.profesorForm.value
      };

      this.usuariosService.actualizarUsuario(this.profesorIdActual, profesorData).subscribe({
        next: () => {
          this.mensaje = 'Profesor actualizado exitosamente';
          this.modoEdicion = false;
          this.profesorIdActual = null;
          this.profesorForm.reset();
          this.cargando = false;
          this.cargarProfesores();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al actualizar profesor';
          this.cargando = false;
        }
      });
    } else {
      // Lógica para crear nuevo profesor
      const profesorData = {
        ...this.profesorForm.value,
        rol_id: 3
      };

      this.usuariosService.crearUsuario(profesorData).subscribe({
        next: () => {
          this.mensaje = 'Profesor registrado exitosamente';
          this.profesorForm.reset();
          this.cargando = false;
          this.cargarProfesores();
        },
        error: (error) => {
          this.error = error.error?.error || 'Error al crear profesor';
          this.cargando = false;
        }
      });
    }
  }

  eliminarProfesor(id: number): void {
    if (confirm('¿Estás seguro de que deseas eliminar este profesor?')) {
      this.usuariosService.eliminarUsuario(id).subscribe({
        next: () => {
          this.cargarProfesores();
        },
        error: (error) => {
          console.error('Error al eliminar profesor:', error);
        }
      });
    }
  }
}
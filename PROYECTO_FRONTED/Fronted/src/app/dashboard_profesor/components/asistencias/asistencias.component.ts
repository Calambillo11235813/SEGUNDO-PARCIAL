import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';

@Component({
  selector: 'app-asistencias',
  templateUrl: './asistencias.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class AsistenciasComponent implements OnInit {
  materias: any[] = [];
  estudiantes: any[] = [];
  asistenciaForm: FormGroup;
  loading = false;
  materiasLoading = false;
  estudiantesLoading = false;
  error = '';
  mensaje = '';
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private materiasService: MateriasService
  ) {
    this.asistenciaForm = this.fb.group({
      materia: [null, Validators.required],
      fecha: [this.obtenerFechaActual(), Validators.required]
    });
  }
  
  ngOnInit(): void {
    this.cargarMaterias();
    
    // Escuchar cambios en el formulario para cargar estudiantes
    this.asistenciaForm.get('materia')?.valueChanges.subscribe(value => {
      if (value) {
        this.cargarEstudiantes();
      }
    });
  }
  
  obtenerFechaActual(): string {
    const hoy = new Date();
    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');
    return `${año}-${mes}-${dia}`;
  }
  
  cargarMaterias(): void {
    this.materiasLoading = true;
    
    // Comentamos la llamada al API real
    /*
    const usuario = this.authService.getCurrentUser();
    
    if (usuario && usuario.id) {
      this.materiasService.getMateriasPorProfesor(usuario.id).subscribe({
        next: (data) => {
          this.materias = data;
          this.materiasLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar materias';
          this.materiasLoading = false;
        }
      });
    } else {
      this.materiasLoading = false;
      this.error = 'No se pudo identificar al profesor';
    }
    */
    
    // Datos simulados para prueba
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
          curso_nombre: 'Octavo A - Básica',
          estudiantes_count: 32
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
          curso_nombre: 'Octavo A - Básica',
          estudiantes_count: 32
        },
        {
          id: 3,
          nombre: 'Ciencias Naturales',
          curso: {
            id: 102,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 8,
            paralelo: 'B'
          },
          curso_nombre: 'Octavo B - Básica',
          estudiantes_count: 30
        },
        {
          id: 4,
          nombre: 'Historia y Geografía',
          curso: {
            id: 103,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 7,
            paralelo: 'A'
          },
          curso_nombre: 'Séptimo A - Básica',
          estudiantes_count: 35
        }
      ];
      this.materiasLoading = false;
    }, 800);
  }
  
  cargarEstudiantes(): void {
    const materiaId = this.asistenciaForm.get('materia')?.value;
    if (!materiaId) return;
    
    this.estudiantesLoading = true;
    this.estudiantes = [];
    
    // Comentamos la llamada al API real
    /*
    this.materiasService.getEstudiantesPorMateria(materiaId).subscribe({
      next: (data) => {
        this.estudiantes = data.map((est: any) => ({
          ...est,
          asistio: true // Por defecto todos asistieron
        }));
        this.estudiantesLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes:', error);
        this.error = 'Error al cargar los estudiantes';
        this.estudiantesLoading = false;
      }
    });
    */
    
    // Datos simulados para prueba
    setTimeout(() => {
      // Generar datos diferentes según la materia seleccionada
      const cantidadEstudiantes = 20 + (materiaId % 5);
      
      for (let i = 1; i <= cantidadEstudiantes; i++) {
        this.estudiantes.push({
          id: i,
          nombre: `Nombre ${i}`,
          apellido: `Apellido ${i}`,
          codigo: `EST${1000 + i}`,
          asistio: true // Por defecto todos asistieron
        });
      }
      
      this.estudiantesLoading = false;
    }, 800);
  }
  
  toggleAsistencia(estudiante: any): void {
    estudiante.asistio = !estudiante.asistio;
  }
  
  guardarAsistencias(): void {
    if (this.asistenciaForm.invalid || this.estudiantes.length === 0) {
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    const asistenciasData = {
      materia_id: this.asistenciaForm.get('materia')?.value,
      fecha: this.asistenciaForm.get('fecha')?.value,
      asistencias: this.estudiantes.map(est => ({
        estudiante_id: est.id,
        asistio: est.asistio
      }))
    };
    
    // Comentamos la llamada al API real
    /*
    this.asistenciasService.guardarAsistencias(asistenciasData).subscribe({
      next: () => {
        this.mensaje = 'Asistencias registradas correctamente';
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al guardar asistencias:', error);
        this.error = 'Error al guardar las asistencias';
        this.loading = false;
      }
    });
    */
    
    // Simulación para prueba
    setTimeout(() => {
      this.mensaje = 'Asistencias registradas correctamente';
      this.loading = false;
    }, 1000);
  }
}
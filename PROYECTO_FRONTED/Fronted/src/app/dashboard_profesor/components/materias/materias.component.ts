import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-materias-profesor',
  templateUrl: './materias.component.html',
  standalone: true,
  imports: [CommonModule]
})
export class MateriasProfesorComponent implements OnInit {
  materias: any[] = [];
  materiasFiltradas: any[] = [];
  loading = false;
  error = '';
  
  constructor(
    private authService: AuthService,
    private materiasService: MateriasService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.cargarMaterias();
  }
  
  cargarMaterias(): void {
    this.loading = true;
    
    // Comentamos la llamada al API real
    /*
    const usuario = this.authService.getCurrentUser();
    
    if (usuario && usuario.id) {
      this.materiasService.getMateriasPorProfesor(usuario.id).subscribe({
        next: (data) => {
          this.materias = data;
          this.materiasFiltradas = [...data];
          this.loading = false;
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar las materias asignadas';
          this.loading = false;
        }
      });
    } else {
      this.loading = false;
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
        },
        {
          id: 5,
          nombre: 'Educación Física',
          curso: {
            id: 104,
            nivel: { id: 2, nombre: 'Bachillerato' },
            grado: 1,
            paralelo: 'C'
          },
          curso_nombre: 'Primero C - Bachillerato',
          estudiantes_count: 28
        }
      ];
      
      this.materiasFiltradas = [...this.materias];
      this.loading = false;
    }, 800); // Simulamos un pequeño retraso para ver el efecto de carga
  }
  
  filtrarMaterias(texto: string): void {
    if (!texto) {
      this.materiasFiltradas = [...this.materias];
      return;
    }
    
    texto = texto.toLowerCase();
    this.materiasFiltradas = this.materias.filter(materia => 
      materia.nombre.toLowerCase().includes(texto) ||
      materia.curso_nombre?.toLowerCase().includes(texto)
    );
  }
  
  verDetalle(materiaId: number): void {
    // Implementar navegación al detalle de la materia
    this.router.navigate(['/profesor/materia', materiaId]);
  }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';

interface MateriasResponse {
  materias?: any[];
  profesor?: string;
  [key: string]: any;  // Permite otras propiedades
}

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
  usuario: any;
  
  constructor(
    private authService: AuthService,
    private materiasService: MateriasService,
    private router: Router
  ) {}
  
  ngOnInit(): void {
    this.usuario = this.authService.getCurrentUser();
    this.cargarMaterias();
  }
  
  cargarMaterias(): void {
    this.loading = true;
    
    if (this.usuario && this.usuario.id) {
      this.materiasService.getMateriasPorProfesor(this.usuario.id).subscribe({
        next: (response: any) => {
          console.log('Materias cargadas:', response);
          
          // Usar type assertion para ayudar a TypeScript
          const data = response as MateriasResponse | any[];
          
          // Verificar si data es un array o un objeto con propiedad materias
          if (Array.isArray(data)) {
            this.materias = data;
          } else {
            // Ahora TypeScript sabe que data puede tener una propiedad 'materias'
            this.materias = data && (data as MateriasResponse).materias ? (data as MateriasResponse).materias || [] : [];
          }
          
          this.materiasFiltradas = [...this.materias];
          this.loading = false;
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar las materias asignadas';
          this.loading = false;
        }
      });
    } else {
      this.error = 'No se pudo identificar al profesor';
      this.loading = false;
    }
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
    this.router.navigate(['/profesor/materia', materiaId]);
  }

  getCursoDisplay(curso: any): string {
    if (!curso) return 'Curso no especificado';
    
    let display = '';
    
    // Si tiene nivel
    if (curso.nivel) {
      display += curso.nivel.nombre + ' - ';
    }
    
    // Si tiene grado y paralelo
    if (curso.grado) {
      display += curso.grado + '° ';
      if (curso.paralelo) {
        display += curso.paralelo;
      }
    }
    
    return display || 'Curso no especificado';
  }
}
import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MateriasService } from '../../../services/materias.service';

@Component({
  selector: 'app-detalle-materia',
  standalone: true,
  imports: [CommonModule, RouterModule],
  template: `
    <div class="p-6">
      <div class="mb-4">
        <button (click)="volver()" class="flex items-center text-red-600 hover:text-red-800">
          <i class="fas fa-arrow-left mr-2"></i> Volver a Mis Materias
        </button>
      </div>
      
      <div *ngIf="loading" class="flex justify-center p-5">
        <div class="h-10 w-10 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
      </div>
      
      <div *ngIf="error" class="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {{ error }}
      </div>
      
      <div *ngIf="materia" class="bg-white rounded-lg shadow-md border border-red-100">
        <div class="p-6 border-b border-red-100">
          <h2 class="text-2xl font-bold text-red-600">{{ materia.nombre }}</h2>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-red-600 mb-3">Información del Curso</h3>
              <ul class="space-y-2">
                <li class="flex items-start">
                  <span class="font-medium w-28">Nivel:</span>
                  <span>{{ cursoDetalle?.nivel_nombre || 'No especificado' }}</span>
                </li>
                <li class="flex items-start">
                  <span class="font-medium w-28">Grado:</span>
                  <span>{{ cursoDetalle?.grado || 'No especificado' }}°</span>
                </li>
                <li class="flex items-start">
                  <span class="font-medium w-28">Paralelo:</span>
                  <span>{{ cursoDetalle?.paralelo || 'No especificado' }}</span>
                </li>
                <li class="flex items-start">
                  <span class="font-medium w-28">Estudiantes:</span>
                  <span>{{ totalEstudiantes }} registrados</span>
                </li>
              </ul>
            </div>
            
            <div>
              <h3 class="text-lg font-semibold text-red-600 mb-3">Acciones Rápidas</h3>
              <div class="space-y-2">
                <a routerLink="/profesor/asistencias" [queryParams]="{materia: materia.id}" 
                  class="flex items-center p-3 rounded-md bg-blue-50 text-blue-700 hover:bg-blue-100 transition">
                  <i class="fas fa-clipboard-check mr-3"></i>
                  <span>Registrar Asistencia</span>
                </a>
                
                <a routerLink="/profesor/notas" [queryParams]="{materia: materia.id}" 
                  class="flex items-center p-3 rounded-md bg-green-50 text-green-700 hover:bg-green-100 transition">
                  <i class="fas fa-chart-line mr-3"></i>
                  <span>Gestionar Calificaciones</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class DetalleMateriaComponent implements OnInit {
  materiaId: number;
  materia: any = null;
  cursoDetalle: any = null;
  totalEstudiantes: any = 0;
  loading = false;
  error = '';
  
  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private materiasService: MateriasService
  ) {
    this.materiaId = 0;
  }
  
  ngOnInit(): void {
    this.route.params.subscribe(params => {
      if (params['id']) {
        this.materiaId = +params['id'];
        this.cargarDetalleMateria();
      }
    });
  }
  
  cargarDetalleMateria(): void {
    this.loading = true;
    this.materiasService.getMateria(this.materiaId).subscribe({
      next: (data) => {
        console.log('Datos de materia:', data);
        this.materia = data;
        
        // Verificar la estructura exacta de los datos para encontrar el curso ID
        let cursoId = null;
        if (data.curso && typeof data.curso === 'object' && data.curso.id) {
          // Si curso es un objeto y tiene un id
          cursoId = data.curso.id;
        } else if (data.curso && typeof data.curso === 'number') {
          // Si curso es directamente el ID
          cursoId = data.curso;
        } else if (data.curso_id) {
          // Si hay un campo específico curso_id
          cursoId = data.curso_id;
        }
        
        if (cursoId) {
          this.cargarDetalleCurso(cursoId);
          this.cargarTotalEstudiantes(cursoId);
        } else {
          console.warn('No se pudo determinar el ID del curso');
          this.loading = false;
        }
      },
      error: (error) => {
        console.error('Error al cargar detalle de materia:', error);
        this.error = 'No se pudo cargar la información de la materia';
        this.loading = false;
      }
    });
  }
  
  cargarDetalleCurso(cursoId: number): void {
    this.materiasService.getCursoDetalle(cursoId).subscribe({
      next: (data) => {
        console.log('Datos del curso:', data);
        this.cursoDetalle = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar detalle del curso:', error);
        this.loading = false;
      }
    });
  }
  
  cargarTotalEstudiantes(cursoId: number): void {
    this.materiasService.getEstudiantesDeCurso(cursoId).subscribe({
      next: (data) => {
        console.log('Datos de estudiantes:', data);
        // Usar el campo total_estudiantes directamente de la respuesta
        if (data && typeof data === 'object' && 'total_estudiantes' in data) {
          this.totalEstudiantes = data.total_estudiantes;
        } else if (data && Array.isArray(data)) {
          // Fallback: si la respuesta es un array, usar su longitud
          this.totalEstudiantes = data.length;
        } else {
          this.totalEstudiantes = 0;
        }
      },
      error: (error) => {
        console.error('Error al cargar el total de estudiantes:', error);
        this.totalEstudiantes = 0;
      }
    });
  }
  
  volver(): void {
    this.router.navigate(['/profesor/materias']);
  }
}
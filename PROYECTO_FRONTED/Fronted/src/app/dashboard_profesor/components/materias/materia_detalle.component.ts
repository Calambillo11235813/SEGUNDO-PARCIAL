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
          <p class="text-gray-600 mt-2">{{ materia.curso_nombre }}</p>
        </div>
        
        <div class="p-6">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 class="text-lg font-semibold text-red-600 mb-3">Información del Curso</h3>
              <ul class="space-y-2">
                <li class="flex items-start">
                  <span class="font-medium w-28">Nivel:</span>
                  <span>{{ materia.curso?.nivel?.nombre || 'No especificado' }}</span>
                </li>
                <li class="flex items-start">
                  <span class="font-medium w-28">Grado:</span>
                  <span>{{ materia.curso?.grado || 'No especificado' }}° {{ materia.curso?.paralelo || '' }}</span>
                </li>
                <li class="flex items-start">
                  <span class="font-medium w-28">Estudiantes:</span>
                  <span>{{ materia.estudiantes_count || 0 }} estudiantes registrados</span>
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
        this.materia = data;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar detalle de materia:', error);
        this.error = 'No se pudo cargar la información de la materia';
        this.loading = false;
      }
    });
  }
  
  volver(): void {
    this.router.navigate(['/profesor/materias']);
  }
}
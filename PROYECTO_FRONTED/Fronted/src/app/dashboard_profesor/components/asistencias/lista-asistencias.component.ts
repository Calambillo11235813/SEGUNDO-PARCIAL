import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AsistenciasService } from '../../../services/asistencias.service';

@Component({
  selector: 'app-lista-asistencias',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="p-6">
      <!-- Header -->
      <div class="mb-6">
        <button (click)="volver()" class="flex items-center text-red-600 hover:text-red-800 mb-4">
          <i class="fas fa-arrow-left mr-2"></i> Volver
        </button>
        
        <h1 class="text-2xl font-bold text-red-600">Lista de Asistencias</h1>
        <p class="text-gray-600" *ngIf="materia">{{ materia.nombre }}</p>
      </div>

      <!-- Filtros -->
      <div class="bg-white rounded-lg shadow-md border border-red-100 p-6 mb-6">
        <h3 class="text-lg font-semibold text-red-600 mb-4">Filtros</h3>
        
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Fecha específica</label>
            <input 
              type="date" 
              [(ngModel)]="filtros.fecha"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Desde</label>
            <input 
              type="date" 
              [(ngModel)]="filtros.desde"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Hasta</label>
            <input 
              type="date" 
              [(ngModel)]="filtros.hasta"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
            >
          </div>
        </div>
        
        <div class="flex gap-2 mt-4">
          <button 
            (click)="aplicarFiltros()" 
            class="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 transition"
          >
            Aplicar Filtros
          </button>
          
          <button 
            (click)="limpiarFiltros()" 
            class="px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition"
          >
            Limpiar
          </button>
        </div>
      </div>

      <!-- Loading -->
      <div *ngIf="loading" class="flex justify-center p-8">
        <div class="h-10 w-10 border-4 border-red-600 border-t-transparent rounded-full animate-spin"></div>
      </div>

      <!-- Error -->
      <div *ngIf="error" class="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        {{ error }}
      </div>

      <!-- Tabla de Asistencias -->
      <div *ngIf="!loading && asistenciasData" class="bg-white rounded-lg shadow-md border border-red-100">
        <div class="p-6 border-b border-red-100">
          <h3 class="text-lg font-semibold text-red-600">
            Asistencias Registradas
            <span class="text-sm text-gray-600 ml-2">({{ getTotalRegistros() }} registros)</span>
          </h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-red-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-red-600 uppercase tracking-wider">
                  Fecha
                </th>
                <th class="px-6 py-3 text-left text-xs font-medium text-red-600 uppercase tracking-wider">
                  Estudiante
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Estado
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Justificada
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <ng-container *ngFor="let fecha of getFechasOrdenadas()">
                <tr *ngFor="let asistencia of asistenciasData.asistencias[fecha]; let i = index"
                    [class.bg-gray-50]="i % 2 === 0">
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ formatearFecha(fecha) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {{ asistencia.estudiante }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span 
                      class="px-2 py-1 text-xs font-semibold rounded-full"
                      [class.bg-green-100]="asistencia.presente"
                      [class.text-green-800]="asistencia.presente"
                      [class.bg-red-100]="!asistencia.presente"
                      [class.text-red-800]="!asistencia.presente"
                    >
                      {{ asistencia.presente ? 'Presente' : 'Ausente' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-center">
                    <span 
                      class="px-2 py-1 text-xs font-semibold rounded-full"
                      [class.bg-blue-100]="asistencia.justificada"
                      [class.text-blue-800]="asistencia.justificada"
                      [class.bg-gray-100]="!asistencia.justificada"
                      [class.text-gray-800]="!asistencia.justificada"
                    >
                      {{ asistencia.justificada ? 'Sí' : 'No' }}
                    </span>
                  </td>
                </tr>
              </ng-container>
            </tbody>
          </table>
        </div>
        
        <!-- Mensaje si no hay datos -->
        <div *ngIf="getTotalRegistros() === 0" class="p-8 text-center text-gray-500">
          <i class="fas fa-clipboard-list text-4xl mb-4"></i>
          <p>No se encontraron registros de asistencia con los filtros aplicados.</p>
        </div>
      </div>

      <!-- Resumen -->
      <div *ngIf="!loading && asistenciasData && getTotalRegistros() > 0" 
           class="bg-white rounded-lg shadow-md border border-red-100 mt-6 p-6">
        <h3 class="text-lg font-semibold text-red-600 mb-4">Resumen</h3>
        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ getContadorPresentes() }}</div>
            <div class="text-sm text-green-600">Presentes</div>
          </div>
          <div class="text-center p-4 bg-red-50 rounded-lg">
            <div class="text-2xl font-bold text-red-600">{{ getContadorAusentes() }}</div>
            <div class="text-sm text-red-600">Ausentes</div>
          </div>
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ getContadorJustificadas() }}</div>
            <div class="text-sm text-blue-600">Justificadas</div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class ListaAsistenciasComponent implements OnInit {
  materiaId: number = 0;
  materia: any = null;
  asistenciasData: any = null;
  loading = false;
  error = '';
  
  filtros = {
    fecha: '',
    desde: '',
    hasta: ''
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private asistenciasService: AsistenciasService
  ) {}

  ngOnInit(): void {
    // Obtener materia ID de los query params
    this.route.queryParams.subscribe(params => {
      if (params['materia']) {
        this.materiaId = +params['materia'];
        this.cargarAsistencias();
      }
    });
  }

  cargarAsistencias(): void {
    if (!this.materiaId) return;
    
    this.loading = true;
    this.error = '';
    
    // Preparar filtros para el servicio
    const filtrosServicio: any = {};
    if (this.filtros.fecha) filtrosServicio.fecha = this.filtros.fecha;
    if (this.filtros.desde) filtrosServicio.desde = this.filtros.desde;
    if (this.filtros.hasta) filtrosServicio.hasta = this.filtros.hasta;
    
    this.asistenciasService.getAsistenciasPorMateria(this.materiaId, filtrosServicio).subscribe({
      next: (data) => {
        console.log('Datos de asistencias:', data);
        this.asistenciasData = data;
        this.materia = data.materia;
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar asistencias:', error);
        this.error = 'No se pudieron cargar las asistencias';
        this.loading = false;
      }
    });
  }

  aplicarFiltros(): void {
    this.cargarAsistencias();
  }

  limpiarFiltros(): void {
    this.filtros = {
      fecha: '',
      desde: '',
      hasta: ''
    };
    this.cargarAsistencias();
  }

  getFechasOrdenadas(): string[] {
    if (!this.asistenciasData?.asistencias) return [];
    return Object.keys(this.asistenciasData.asistencias).sort((a, b) => 
      new Date(b).getTime() - new Date(a).getTime()
    );
  }

  getTotalRegistros(): number {
    if (!this.asistenciasData?.asistencias) return 0;
    return Object.values(this.asistenciasData.asistencias)
      .reduce((total: number, asistencias: any) => total + asistencias.length, 0);
  }

  getContadorPresentes(): number {
    if (!this.asistenciasData?.asistencias) return 0;
    let contador = 0;
    Object.values(this.asistenciasData.asistencias).forEach((asistencias: any) => {
      contador += asistencias.filter((a: any) => a.presente).length;
    });
    return contador;
  }

  getContadorAusentes(): number {
    if (!this.asistenciasData?.asistencias) return 0;
    let contador = 0;
    Object.values(this.asistenciasData.asistencias).forEach((asistencias: any) => {
      contador += asistencias.filter((a: any) => !a.presente).length;
    });
    return contador;
  }

  getContadorJustificadas(): number {
    if (!this.asistenciasData?.asistencias) return 0;
    let contador = 0;
    Object.values(this.asistenciasData.asistencias).forEach((asistencias: any) => {
      contador += asistencias.filter((a: any) => a.justificada).length;
    });
    return contador;
  }

  formatearFecha(fecha: string): string {
    const fechaObj = new Date(fecha + 'T00:00:00');
    return fechaObj.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  volver(): void {
    this.router.navigate(['/profesor/materias', this.materiaId]);
  }
}
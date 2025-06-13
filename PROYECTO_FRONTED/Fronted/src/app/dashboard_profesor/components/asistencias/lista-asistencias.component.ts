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
        
        <h1 class="text-2xl font-bold text-red-600">Detalle de Asistencia</h1>
        <div class="mt-2">
          <p class="text-gray-600" *ngIf="materia">{{ materia.nombre }}</p>
          <p class="text-lg font-semibold text-gray-800" *ngIf="fechaSeleccionada">
            {{ formatearFecha(fechaSeleccionada) }}
          </p>
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

      <!-- Resumen del día -->
      <div *ngIf="!loading && asistenciasDelDia.length > 0" 
           class="bg-white rounded-lg shadow-md border border-red-100 mb-6 p-6">
        <h3 class="text-lg font-semibold text-red-600 mb-4">Resumen del día</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ asistenciasDelDia.length }}</div>
            <div class="text-sm text-blue-600">Total Estudiantes</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ getContadorPresentes() }}</div>
            <div class="text-sm text-green-600">Presentes</div>
          </div>
          <div class="text-center p-4 bg-red-50 rounded-lg">
            <div class="text-2xl font-bold text-red-600">{{ getContadorAusentes() }}</div>
            <div class="text-sm text-red-600">Ausentes</div>
          </div>
          <div class="text-center p-4 bg-yellow-50 rounded-lg">
            <div class="text-2xl font-bold text-yellow-600">{{ getContadorJustificadas() }}</div>
            <div class="text-sm text-yellow-600">Justificadas</div>
          </div>
        </div>
      </div>

      <!-- Lista detallada de estudiantes -->
      <div *ngIf="!loading && asistenciasDelDia.length > 0" class="bg-white rounded-lg shadow-md border border-red-100">
        <div class="p-6 border-b border-red-100">
          <h3 class="text-lg font-semibold text-red-600">
            Lista de Estudiantes
          </h3>
        </div>
        
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-red-50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-red-600 uppercase tracking-wider">
                  #
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
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Observaciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr *ngFor="let asistencia of asistenciasDelDia; let i = index"
                  [class.bg-gray-50]="i % 2 === 0"
                  [class.bg-red-50]="!asistencia.presente && !asistencia.justificada"
                  [class.bg-green-50]="asistencia.presente">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">
                  {{ i + 1 }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  <div class="flex items-center">
                    <div class="flex-shrink-0 h-10 w-10">
                      <div class="h-10 w-10 rounded-full bg-red-500 flex items-center justify-center">
                        <span class="text-sm font-medium text-white">
                          {{ getInitials(asistencia.estudiante) }}
                        </span>
                      </div>
                    </div>
                    <div class="ml-4">
                      <div class="text-sm font-medium text-gray-900">
                        {{ asistencia.estudiante }}
                      </div>
                    </div>
                  </div>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span 
                    class="px-3 py-1 text-xs font-semibold rounded-full flex items-center justify-center w-20 mx-auto"
                    [class.bg-green-100]="asistencia.presente"
                    [class.text-green-800]="asistencia.presente"
                    [class.bg-red-100]="!asistencia.presente"
                    [class.text-red-800]="!asistencia.presente"
                  >
                    <i class="fas mr-1" 
                       [class.fa-check]="asistencia.presente"
                       [class.fa-times]="!asistencia.presente"></i>
                    {{ asistencia.presente ? 'Presente' : 'Ausente' }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span 
                    class="px-3 py-1 text-xs font-semibold rounded-full flex items-center justify-center w-16 mx-auto"
                    [class.bg-blue-100]="asistencia.justificada"
                    [class.text-blue-800]="asistencia.justificada"
                    [class.bg-gray-100]="!asistencia.justificada"
                    [class.text-gray-800]="!asistencia.justificada"
                  >
                    <i class="fas mr-1" 
                       [class.fa-check]="asistencia.justificada"
                       [class.fa-times]="!asistencia.justificada"></i>
                    {{ asistencia.justificada ? 'Sí' : 'No' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-500 max-w-xs">
                  <span *ngIf="asistencia.observaciones" class="truncate block">
                    {{ asistencia.observaciones }}
                  </span>
                  <span *ngIf="!asistencia.observaciones" class="text-gray-400 italic">
                    Sin observaciones
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Mensaje si no hay datos -->
        <div *ngIf="asistenciasDelDia.length === 0" class="p-8 text-center text-gray-500">
          <i class="fas fa-clipboard-list text-4xl mb-4"></i>
          <p>No se encontraron registros de asistencia para esta fecha.</p>
        </div>
      </div>

      <!-- Acciones -->
      <div *ngIf="!loading && asistenciasDelDia.length > 0" class="mt-6 flex justify-end gap-4">
        <button 
          (click)="exportarPDF()"
          class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition flex items-center"
        >
          <i class="fas fa-file-pdf mr-2"></i>
          Exportar PDF
        </button>
        
        <button 
          (click)="editarAsistencia()"
          class="px-4 py-2 bg-yellow-600 text-white rounded-md hover:bg-yellow-700 transition flex items-center"
        >
          <i class="fas fa-edit mr-2"></i>
          Editar Asistencia
        </button>
      </div>
    </div>
  `
})
export class ListaAsistenciasComponent implements OnInit {
  materiaId: number = 0;
  fechaSeleccionada: string = '';
  materia: any = null;
  asistenciasDelDia: any[] = [];
  loading = false;
  error = '';

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private asistenciasService: AsistenciasService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['materia'] && params['fecha']) {
        this.materiaId = +params['materia'];
        this.fechaSeleccionada = params['fecha'];
        this.cargarAsistenciasDelDia();
      }
    });
  }

  cargarAsistenciasDelDia(): void {
    if (!this.materiaId || !this.fechaSeleccionada) return;
    
    this.loading = true;
    this.error = '';
    
    const filtros = {
      fecha: this.fechaSeleccionada
    };
    
    this.asistenciasService.getAsistenciasPorMateria(this.materiaId, filtros).subscribe({
      next: (data) => {
        console.log('Datos de asistencias del día:', data);
        this.materia = data.materia;
        
        if (data.asistencias && data.asistencias[this.fechaSeleccionada]) {
          this.asistenciasDelDia = data.asistencias[this.fechaSeleccionada];
        } else {
          this.asistenciasDelDia = [];
        }
        
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar asistencias del día:', error);
        this.error = 'No se pudieron cargar las asistencias del día';
        this.loading = false;
      }
    });
  }

  getContadorPresentes(): number {
    return this.asistenciasDelDia.filter(a => a.presente).length;
  }

  getContadorAusentes(): number {
    return this.asistenciasDelDia.filter(a => !a.presente).length;
  }

  getContadorJustificadas(): number {
    return this.asistenciasDelDia.filter(a => a.justificada).length;
  }

  getInitials(nombre: string): string {
    return nombre.split(' ')
      .map(n => n.charAt(0))
      .join('')
      .substring(0, 2)
      .toUpperCase();
  }

  formatearFecha(fecha: string): string {
    const fechaObj = new Date(fecha + 'T00:00:00');
    return fechaObj.toLocaleDateString('es-ES', {
      weekday: 'long',
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  }

  exportarPDF(): void {
    // Implementar exportación a PDF
    console.log('Exportar PDF de asistencia del día:', this.fechaSeleccionada);
  }

  editarAsistencia(): void {
    // Navegar a edición de asistencia
    this.router.navigate(['/profesor/asistencias/editar'], {
      queryParams: { 
        materia: this.materiaId,
        fecha: this.fechaSeleccionada
      }
    });
  }

  volver(): void {
    this.router.navigate(['/profesor/asistencias/registro'], {
      queryParams: { materia: this.materiaId }
    });
  }
}
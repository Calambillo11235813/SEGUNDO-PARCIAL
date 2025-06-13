import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { AsistenciasService } from '../../../services/asistencias.service';

@Component({
  selector: 'app-registro-asistencias',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  template: `
    <div class="p-6">
      <!-- Header -->
      <div class="mb-6">
        <button (click)="volver()" class="flex items-center text-red-600 hover:text-red-800 mb-4">
          <i class="fas fa-arrow-left mr-2"></i> Volver
        </button>
        
        <h1 class="text-2xl font-bold text-red-600">Registros de Asistencia</h1>
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
              placeholder="dd/mm/aaaa"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Desde</label>
            <input 
              type="date" 
              [(ngModel)]="filtros.desde"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="dd/mm/aaaa"
            >
          </div>
          
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-2">Hasta</label>
            <input 
              type="date" 
              [(ngModel)]="filtros.hasta"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
              placeholder="dd/mm/aaaa"
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

      <!-- Registros de Asistencias -->
      <div *ngIf="!loading && registrosAgrupados.length > 0" class="bg-white rounded-lg shadow-md border border-red-100">
        <div class="p-6 border-b border-red-100">
          <h3 class="text-lg font-semibold text-red-600">
            Asistencias Registradas
            <span class="text-sm text-gray-600 ml-2">({{ registrosAgrupados.length }} registros)</span>
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
                  Trimestre
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Presentes
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Ausentes
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Justificadas
                </th>
                <th class="px-6 py-3 text-center text-xs font-medium text-red-600 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr *ngFor="let registro of registrosAgrupados; let i = index"
                  [class.bg-gray-50]="i % 2 === 0"
                  class="hover:bg-red-50 cursor-pointer transition-colors">
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ formatearFecha(registro.fecha) }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  {{ registro.trimestre }}
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span class="text-green-600 font-semibold">{{ registro.presentes }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span class="text-red-600 font-semibold">{{ registro.ausentes }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <span class="text-blue-600 font-semibold">{{ registro.justificadas }}</span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-center">
                  <button 
                    (click)="verDetalle(registro.fecha)"
                    class="text-red-600 hover:text-red-800 font-medium"
                  >
                    Ver Detalle
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Mensaje si no hay datos -->
        <div *ngIf="registrosAgrupados.length === 0" class="p-8 text-center text-gray-500">
          <i class="fas fa-clipboard-list text-4xl mb-4"></i>
          <p>No se encontraron registros de asistencia con los filtros aplicados.</p>
        </div>
      </div>

      <!-- Resumen Total -->
      <div *ngIf="!loading && registrosAgrupados.length > 0" 
           class="bg-white rounded-lg shadow-md border border-red-100 mt-6 p-6">
        <h3 class="text-lg font-semibold text-red-600 mb-4">Resumen Total</h3>
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div class="text-center p-4 bg-blue-50 rounded-lg">
            <div class="text-2xl font-bold text-blue-600">{{ registrosAgrupados.length }}</div>
            <div class="text-sm text-blue-600">Registros</div>
          </div>
          <div class="text-center p-4 bg-green-50 rounded-lg">
            <div class="text-2xl font-bold text-green-600">{{ getTotalPresentes() }}</div>
            <div class="text-sm text-green-600">Total Presentes</div>
          </div>
          <div class="text-center p-4 bg-red-50 rounded-lg">
            <div class="text-2xl font-bold text-red-600">{{ getTotalAusentes() }}</div>
            <div class="text-sm text-red-600">Total Ausentes</div>
          </div>
          <div class="text-center p-4 bg-yellow-50 rounded-lg">
            <div class="text-2xl font-bold text-yellow-600">{{ getTotalJustificadas() }}</div>
            <div class="text-sm text-yellow-600">Total Justificadas</div>
          </div>
        </div>
      </div>
    </div>
  `
})
export class RegistroAsistenciasComponent implements OnInit {
  materiaId: number = 0;
  materia: any = null;
  asistenciasData: any = null;
  registrosAgrupados: any[] = [];
  loading = false;
  error = '';
  
  filtros = {
    fecha: '',
    desde: '',
    hasta: ''
  };

  private readonly anoActual: number = new Date().getFullYear();

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private asistenciasService: AsistenciasService
  ) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['materia']) {
        this.materiaId = +params['materia'];
        this.cargarAsistencias();
      }
    });
  }

  private esDelAnoActual(fecha: string): boolean {
    if (!fecha) return false;
    const anoFecha = new Date(fecha).getFullYear();
    return anoFecha === this.anoActual;
  }

  cargarAsistencias(): void {
    if (!this.materiaId) return;
    
    this.loading = true;
    this.error = '';
    
    const filtrosServicio: any = {};
    if (this.filtros.fecha) filtrosServicio.fecha = this.filtros.fecha;
    if (this.filtros.desde) filtrosServicio.desde = this.filtros.desde;
    if (this.filtros.hasta) filtrosServicio.hasta = this.filtros.hasta;
    
    if (!this.filtros.fecha && !this.filtros.desde && !this.filtros.hasta) {
      filtrosServicio.desde = `${this.anoActual}-01-01`;
      filtrosServicio.hasta = `${this.anoActual}-12-31`;
    }
    
    this.asistenciasService.getAsistenciasPorMateria(this.materiaId, filtrosServicio).subscribe({
      next: (data) => {
        console.log('Datos de asistencias:', data);
        
        if (data && data.asistencias && !this.filtros.fecha && !this.filtros.desde && !this.filtros.hasta) {
          const asistenciasFiltradas: any = {};
          
          Object.keys(data.asistencias).forEach(fecha => {
            if (this.esDelAnoActual(fecha)) {
              asistenciasFiltradas[fecha] = data.asistencias[fecha];
            }
          });
          
          data.asistencias = asistenciasFiltradas;
        }
        
        this.asistenciasData = data;
        this.materia = data.materia;
        this.agruparRegistros();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al cargar asistencias:', error);
        this.error = 'No se pudieron cargar las asistencias';
        this.loading = false;
      }
    });
  }

  private agruparRegistros(): void {
    if (!this.asistenciasData?.asistencias) {
      this.registrosAgrupados = [];
      return;
    }

    this.registrosAgrupados = Object.keys(this.asistenciasData.asistencias)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime())
      .map(fecha => {
        const asistencias = this.asistenciasData.asistencias[fecha];
        const presentes = asistencias.filter((a: any) => a.presente).length;
        const ausentes = asistencias.filter((a: any) => !a.presente).length;
        const justificadas = asistencias.filter((a: any) => a.justificada).length;
        
        return {
          fecha,
          trimestre: this.obtenerTrimestre(fecha),
          presentes,
          ausentes,
          justificadas,
          total: asistencias.length
        };
      });
  }

  private obtenerTrimestre(fecha: string): string {
    const fechaObj = new Date(fecha);
    const mes = fechaObj.getMonth() + 1;
    const ano = fechaObj.getFullYear();
    
    if (mes >= 1 && mes <= 4) {
      return `Primer Trimestre ${ano}`;
    } else if (mes >= 5 && mes <= 8) {
      return `Segundo Trimestre ${ano}`;
    } else {
      return `Tercer Trimestre ${ano}`;
    }
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

  getTotalPresentes(): number {
    return this.registrosAgrupados.reduce((total, registro) => total + registro.presentes, 0);
  }

  getTotalAusentes(): number {
    return this.registrosAgrupados.reduce((total, registro) => total + registro.ausentes, 0);
  }

  getTotalJustificadas(): number {
    return this.registrosAgrupados.reduce((total, registro) => total + registro.justificadas, 0);
  }

  formatearFecha(fecha: string): string {
    const fechaObj = new Date(fecha + 'T00:00:00');
    return fechaObj.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  verDetalle(fecha: string): void {
    this.router.navigate(['/profesor/asistencias/detalle'], {
      queryParams: { 
        materia: this.materiaId,
        fecha: fecha
      }
    });
  }

  volver(): void {
    this.router.navigate(['/profesor/materia/', this.materiaId]);
  }
}
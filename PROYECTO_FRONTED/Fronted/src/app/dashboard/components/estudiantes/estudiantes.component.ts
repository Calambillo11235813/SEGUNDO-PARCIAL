import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-estudiantes',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="estudiantes-container">
      <h2>Gestión de Estudiantes</h2>
      
      <div class="row">
        <div class="col-md-4">
          <div class="card">
            <div class="card-header">
              <h3>Nuevo Estudiante</h3>
            </div>
            <div class="card-body">
              <form [formGroup]="estudianteForm" (ngSubmit)="crearEstudiante()">
                <div class="form-group">
                  <label for="codigo">Código</label>
                  <input type="text" id="codigo" formControlName="codigo" class="form-control">
                </div>
                
                <div class="form-group">
                  <label for="nombre">Nombre</label>
                  <input type="text" id="nombre" formControlName="nombre" class="form-control">
                </div>
                
                <div class="form-group">
                  <label for="apellido">Apellido</label>
                  <input type="text" id="apellido" formControlName="apellido" class="form-control">
                </div>
                
                <div class="form-group">
                  <label for="telefono">Teléfono</label>
                  <input type="text" id="telefono" formControlName="telefono" class="form-control">
                </div>
                
                <div class="form-group">
                  <label for="password">Contraseña</label>
                  <input type="password" id="password" formControlName="password" class="form-control">
                </div>
                
                <div *ngIf="mensaje" class="alert alert-success">
                  {{ mensaje }}
                </div>
                
                <div *ngIf="error" class="alert alert-danger">
                  {{ error }}
                </div>
                
                <button type="submit" class="btn btn-primary" [disabled]="estudianteForm.invalid || loading">
                  <span *ngIf="loading" class="spinner-border spinner-border-sm mr-1"></span>
                  Registrar Estudiante
                </button>
              </form>
            </div>
          </div>
        </div>
        
        <div class="col-md-8">
          <div class="card">
            <div class="card-header">
              <h3>Lista de Estudiantes</h3>
            </div>
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Nombre</th>
                    <th>Apellido</th>
                    <th>Teléfono</th>
                  </tr>
                </thead>
                <tbody>
                  <tr *ngFor="let estudiante of estudiantes">
                    <td>{{ estudiante.codigo }}</td>
                    <td>{{ estudiante.nombre }}</td>
                    <td>{{ estudiante.apellido }}</td>
                    <td>{{ estudiante.telefono || 'N/A' }}</td>
                  </tr>
                  <tr *ngIf="estudiantes.length === 0">
                    <td colspan="4" class="text-center">No hay estudiantes registrados</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .estudiantes-container {
      padding: 1rem;
    }
    .row {
      display: flex;
      flex-wrap: wrap;
      margin: -0.5rem;
    }
    .col-md-4 {
      flex: 0 0 33.333333%;
      max-width: 33.333333%;
      padding: 0.5rem;
    }
    .col-md-8 {
      flex: 0 0 66.666667%;
      max-width: 66.666667%;
      padding: 0.5rem;
    }
    .card {
      border: 1px solid #ddd;
      border-radius: 4px;
      margin-bottom: 1rem;
    }
    .card-header {
      padding: 0.75rem 1.25rem;
      background-color: #f8f9fa;
      border-bottom: 1px solid #ddd;
    }
    .card-body {
      padding: 1.25rem;
    }
    .form-group {
      margin-bottom: 1rem;
    }
    .form-control {
      display: block;
      width: 100%;
      padding: 0.375rem 0.75rem;
      font-size: 1rem;
      border: 1px solid #ced4da;
      border-radius: 0.25rem;
    }
    .btn {
      padding: 0.375rem 0.75rem;
      border-radius: 0.25rem;
      cursor: pointer;
    }
    .btn-primary {
      color: #fff;
      background-color: #007bff;
      border-color: #007bff;
    }
    .btn:disabled {
      opacity: 0.65;
      cursor: not-allowed;
    }
    .alert {
      padding: 0.75rem 1.25rem;
      margin-bottom: 1rem;
      border: 1px solid transparent;
      border-radius: 0.25rem;
    }
    .alert-success {
      color: #155724;
      background-color: #d4edda;
      border-color: #c3e6cb;
    }
    .alert-danger {
      color: #721c24;
      background-color: #f8d7da;
      border-color: #f5c6cb;
    }
    .table {
      width: 100%;
      border-collapse: collapse;
    }
    .table th, .table td {
      padding: 0.75rem;
      border-top: 1px solid #dee2e6;
    }
    .text-center {
      text-align: center;
    }
  `]
})
export class EstudiantesComponent implements OnInit {
  estudianteForm: FormGroup;
  estudiantes: any[] = [];
  loading = false;
  mensaje = '';
  error = '';
  
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
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Error al cargar estudiantes';
        this.loading = false;
      }
    });
  }
  
  crearEstudiante(): void {
    if (this.estudianteForm.invalid) {
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    // Añadir rol_id para estudiante
    const estudianteData = {
      ...this.estudianteForm.value,
      rol_id: 3 // ID del rol estudiante (ajustar según tu base de datos)
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
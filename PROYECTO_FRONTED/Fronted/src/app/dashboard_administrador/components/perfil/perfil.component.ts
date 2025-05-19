import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  template: `
    <div class="perfil-container">
      <h2>Mi Perfil</h2>
      
      <div class="card">
        <div class="card-body">
          <div *ngIf="usuario">
            <h3>{{usuario.nombre}} {{usuario.apellido}}</h3>
            <p><strong>Código:</strong> {{usuario.codigo}}</p>
            <p><strong>Rol:</strong> {{usuario.rol?.nombre || 'Sin rol asignado'}}</p>
            <p><strong>Teléfono:</strong> {{usuario.telefono || 'No registrado'}}</p>
          </div>
          
          <div *ngIf="!usuario" class="alert alert-warning">
            No se pudo cargar la información del perfil.
          </div>
        </div>
      </div>
      
      <div class="card mt-4">
        <div class="card-header">
          <h3>Cambiar Contraseña</h3>
        </div>
        <div class="card-body">
          <form [formGroup]="passwordForm" (ngSubmit)="cambiarPassword()">
            <div class="form-group">
              <label for="currentPassword">Contraseña Actual</label>
              <input type="password" id="currentPassword" formControlName="currentPassword" class="form-control">
            </div>
            
            <div class="form-group">
              <label for="newPassword">Nueva Contraseña</label>
              <input type="password" id="newPassword" formControlName="newPassword" class="form-control">
            </div>
            
            <div class="form-group">
              <label for="confirmPassword">Confirmar Nueva Contraseña</label>
              <input type="password" id="confirmPassword" formControlName="confirmPassword" class="form-control">
            </div>
            
            <div *ngIf="mensaje" class="alert alert-success">
              {{ mensaje }}
            </div>
            
            <div *ngIf="error" class="alert alert-danger">
              {{ error }}
            </div>
            
            <button type="submit" class="btn btn-primary" [disabled]="passwordForm.invalid || loading">
              <span *ngIf="loading" class="spinner-border spinner-border-sm mr-1"></span>
              Actualizar Contraseña
            </button>
          </form>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .perfil-container {
      padding: 1rem;
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
    .alert-warning {
      color: #856404;
      background-color: #fff3cd;
      border-color: #ffeeba;
    }
    .mt-4 {
      margin-top: 1.5rem;
    }
  `]
})
export class PerfilComponent implements OnInit {
  passwordForm: FormGroup;
  usuario: any;
  loading = false;
  mensaje = '';
  error = '';
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private usuariosService: UsuariosService
  ) {
    this.passwordForm = this.fb.group({
      currentPassword: ['', [Validators.required]],
      newPassword: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, {
      validators: this.passwordsMatch
    });
  }
  
  ngOnInit(): void {
    this.cargarPerfil();
  }
  
  cargarPerfil(): void {
    this.usuario = this.authService.getCurrentUser();
  }
  
  passwordsMatch(formGroup: FormGroup): {notMatch: boolean} | null {
    const newPassword = formGroup.get('newPassword')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    
    return newPassword === confirmPassword ? null : { notMatch: true };
  }
  
  cambiarPassword(): void {
    if (this.passwordForm.invalid) {
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    const passwordData = {
      current_password: this.passwordForm.value.currentPassword,
      password: this.passwordForm.value.newPassword
    };
    
    this.usuariosService.actualizarUsuario(this.usuario.id, passwordData).subscribe({
      next: (response: any) => {
        this.mensaje = 'Contraseña actualizada con éxito';
        this.passwordForm.reset();
        this.loading = false;
      },
      error: (err: any) => {
        this.error = err.error?.error || 'Error al actualizar la contraseña';
        this.loading = false;
      }
    });
  }
}
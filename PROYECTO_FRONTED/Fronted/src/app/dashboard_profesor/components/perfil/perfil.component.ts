import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-perfil-profesor',
  templateUrl: './perfil.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class PerfilProfesorComponent implements OnInit {
  passwordForm: FormGroup;
  usuario: any;
  passwordLoading = false;
  mensaje = '';
  error = '';
  mostrarPassword = false;
  mostrarPasswordActual = false;
  mostrarConfirmPassword = false;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private usuariosService: UsuariosService
  ) {
    this.passwordForm = this.fb.group({
      passwordActual: ['', [Validators.required]],
      passwordNuevo: ['', [Validators.required, Validators.minLength(6)]],
      confirmPassword: ['', [Validators.required]]
    }, {
      validators: this.passwordsMatch
    });
  }
  
  ngOnInit(): void {
    this.cargarDatosUsuario();
  }
  
  cargarDatosUsuario(): void {
    const usuarioActual = this.authService.getCurrentUser();
    
    if (usuarioActual && usuarioActual.id) {
      // Obtener datos completos del usuario desde el API
      this.usuariosService.getUsuario(usuarioActual.id).subscribe({
        next: (usuarioCompleto) => {
          this.usuario = usuarioCompleto;
        },
        error: (err) => {
          console.error('Error al cargar el perfil completo:', err);
          // Usar los datos básicos como fallback
          this.usuario = usuarioActual;
        }
      });
    } else {
      this.usuario = usuarioActual;
    }
  }
  
  passwordsMatch(formGroup: FormGroup): {notMatch: boolean} | null {
    const newPassword = formGroup.get('passwordNuevo')?.value;
    const confirmPassword = formGroup.get('confirmPassword')?.value;
    
    return newPassword === confirmPassword ? null : { notMatch: true };
  }
  
  cambiarPassword(): void {
    if (this.passwordForm.invalid) {
      Object.keys(this.passwordForm.controls).forEach(key => {
        this.passwordForm.get(key)?.markAsTouched();
      });
      return;
    }
    
    this.passwordLoading = true;
    this.mensaje = '';
    this.error = '';
    
    const passwordData = {
      passwordActual: this.passwordForm.value.passwordActual,
      passwordNuevo: this.passwordForm.value.passwordNuevo
    };
    
    this.usuariosService.cambiarPassword(this.usuario.id, passwordData).subscribe({
      next: () => {
        this.mensaje = 'Contraseña actualizada correctamente';
        this.passwordLoading = false;
        this.passwordForm.reset();
      },
      error: (error) => {
        console.error('Error al cambiar contraseña:', error);
        this.error = error.error?.error || 'Error al cambiar la contraseña';
        this.passwordLoading = false;
      }
    });
  }
  
  togglePasswordVisibility(field: string): void {
    if (field === 'actual') {
      this.mostrarPasswordActual = !this.mostrarPasswordActual;
    } else if (field === 'nuevo') {
      this.mostrarPassword = !this.mostrarPassword;
    } else if (field === 'confirm') {
      this.mostrarConfirmPassword = !this.mostrarConfirmPassword;
    }
  }
}
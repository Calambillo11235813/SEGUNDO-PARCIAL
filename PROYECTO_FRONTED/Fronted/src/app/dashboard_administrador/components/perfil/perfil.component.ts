import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { UsuariosService } from '../../../services/usuarios.service';

@Component({
  selector: 'app-perfil',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './perfil.component.html'
})
export class PerfilComponent implements OnInit {
  passwordForm: FormGroup;
  usuario: any;
  loading = false;
  mensaje = '';
  error = '';
  mostrarPassword = false;
  mostrarNewPassword = false;
  mostrarConfirmPassword = false;
  
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
    const usuarioActual = this.authService.getCurrentUser();
    
    if (usuarioActual && usuarioActual.id) {
      // Obtener datos completos del usuario desde el API
      this.usuariosService.getUsuario(usuarioActual.id).subscribe({
        next: (usuarioCompleto) => {
          this.usuario = usuarioCompleto;
          console.log('Datos completos:', this.usuario);
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
  
  togglePasswordVisibility(field: string): void {
    if (field === 'current') {
      this.mostrarPassword = !this.mostrarPassword;
    } else if (field === 'new') {
      this.mostrarNewPassword = !this.mostrarNewPassword;
    } else if (field === 'confirm') {
      this.mostrarConfirmPassword = !this.mostrarConfirmPassword;
    }
  }
}
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
  perfilForm: FormGroup;
  passwordForm: FormGroup;
  usuario: any;
  loading = false;
  passwordLoading = false;
  mensaje = '';
  error = '';
  mensajePassword = '';
  errorPassword = '';
  mostrarPassword = false;
  mostrarPasswordActual = false;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private usuariosService: UsuariosService
  ) {
    this.perfilForm = this.fb.group({
      nombre: ['', Validators.required],
      apellido: ['', Validators.required],
      telefono: ['', Validators.pattern('^[0-9]{8}$')]
    });
    
    this.passwordForm = this.fb.group({
      passwordActual: ['', [Validators.required, Validators.minLength(6)]],
      passwordNuevo: ['', [Validators.required, Validators.minLength(6)]]
    });
  }
  
  ngOnInit(): void {
    this.cargarDatosUsuario();
  }
  
  cargarDatosUsuario(): void {
    this.usuario = this.authService.getCurrentUser();
    
    if (this.usuario) {
      this.perfilForm.patchValue({
        nombre: this.usuario.nombre,
        apellido: this.usuario.apellido,
        telefono: this.usuario.telefono
      });
    }
  }
  
  actualizarPerfil(): void {
    if (this.perfilForm.invalid) {
      Object.keys(this.perfilForm.controls).forEach(key => {
        this.perfilForm.get(key)?.markAsTouched();
      });
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    const datosActualizados = this.perfilForm.value;
    
    this.usuariosService.actualizarUsuario(this.usuario.id, datosActualizados).subscribe({
      next: (response) => {
        this.mensaje = 'Perfil actualizado correctamente';
        this.loading = false;
        
        // Actualizar datos en el localStorage
        const usuarioActualizado = {
          ...this.usuario,
          ...datosActualizados
        };
        this.authService.updateUserData(usuarioActualizado);
        this.usuario = usuarioActualizado;
      },
      error: (error) => {
        console.error('Error al actualizar perfil:', error);
        this.error = 'Error al actualizar los datos del perfil';
        this.loading = false;
      }
    });
  }
  
  cambiarPassword(): void {
    if (this.passwordForm.invalid) {
      Object.keys(this.passwordForm.controls).forEach(key => {
        this.passwordForm.get(key)?.markAsTouched();
      });
      return;
    }
    
    this.passwordLoading = true;
    this.mensajePassword = '';
    this.errorPassword = '';
    
    const datosPassword = this.passwordForm.value;
    
    this.usuariosService.cambiarPassword(this.usuario.id, datosPassword).subscribe({
      next: () => {
        this.mensajePassword = 'Contraseña actualizada correctamente';
        this.passwordLoading = false;
        this.passwordForm.reset();
      },
      error: (error) => {
        console.error('Error al cambiar contraseña:', error);
        this.errorPassword = error.error?.error || 'Error al cambiar la contraseña';
        this.passwordLoading = false;
      }
    });
  }
}
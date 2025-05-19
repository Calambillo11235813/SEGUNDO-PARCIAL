import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-login',
  standalone: true,  // El componente es standalone
  imports: [CommonModule, ReactiveFormsModule, RouterLink],  // Importa los módulos necesarios
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';
  loading: boolean = false;

  constructor(
    private authService: AuthService,
    private fb: FormBuilder
  ) {
    this.loginForm = this.fb.group({
      codigo: ['', Validators.required],
      password: ['', Validators.required]
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.loading = true;
    this.errorMessage = '';

    const credentials = this.loginForm.value;
    this.authService.login(credentials).subscribe({
      next: (response) => {
        this.loading = false;
        console.log('Login exitoso', response);
        // Aquí puedes redirigir al usuario
      },
      error: (error) => {
        this.loading = false;
        console.error('Error en login', error);
        this.errorMessage = error.error?.error || 'Credenciales inválidas';
      }
    });
  }
}

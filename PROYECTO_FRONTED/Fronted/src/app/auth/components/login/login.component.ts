import { Component } from '@angular/core';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router'; // Añadir Router
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, RouterLink]
})
export class LoginComponent {
  loginForm: FormGroup;
  errorMessage: string = '';
  loading: boolean = false;

  constructor(
    private authService: AuthService,
    private fb: FormBuilder,
    private router: Router // Añadir el Router
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
        
        // Redirigir según el rol del usuario
        if (this.authService.isAdmin()) {
          this.router.navigate(['/admin/home']);
        } else if (this.authService.isTeacher()) {
          this.router.navigate(['/profesor/home']);
        } else {
          // Ruta predeterminada o ruta para estudiantes
          this.router.navigate(['/admin/home']); // O la ruta predeterminada que corresponda
        }
      },
      error: (error) => {
        this.loading = false;
        console.error('Error en login', error);
        this.errorMessage = error.error?.error || 'Credenciales inválidas';
      }
    });
  }
}

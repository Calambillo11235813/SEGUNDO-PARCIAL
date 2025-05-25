import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { SidebarComponent } from './components/sidebar/sidebar.component';

@Component({
  selector: 'app-dashboard-profesor',
  templateUrl: './dashboard.component.html',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, SidebarComponent]
})
export class DashboardProfesorComponent implements OnInit {
  usuario: any;
  isProfesor = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.usuario = this.authService.getCurrentUser();
    
    // Verificar si es profesor
    if (this.usuario && this.usuario.rol) {
      this.isProfesor = this.usuario.rol.nombre === 'Profesor';
    }
    
    // Redireccionar si no está autenticado o no es profesor
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
    } else if (!this.authService.isTeacher()) {
      this.router.navigate(['/acceso-denegado']);
    }
  }
}
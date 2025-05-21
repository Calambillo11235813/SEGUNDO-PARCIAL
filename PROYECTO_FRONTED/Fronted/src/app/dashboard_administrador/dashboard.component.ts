import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router, RouterModule, RouterOutlet } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { SidebarComponent } from './components/sidebar/sidebar.component';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  standalone: true,
  imports: [CommonModule, RouterModule, RouterOutlet, SidebarComponent]
})
export class DashboardComponent implements OnInit {
  usuario: any;
  isAdmin = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.usuario = this.authService.getCurrentUser();
    console.log('Usuario en dashboard:', this.usuario); // Para debugging
    
    // Verificar si es administrador
    if (this.usuario && this.usuario.rol) {
      console.log('Rol del usuario:', this.usuario.rol); // Para debugging
      this.isAdmin = this.usuario.rol.nombre === 'Administrador';
      console.log('Es admin:', this.isAdmin); // Para debugging
    }
    
    // Redireccionar si no está autenticado
    if (!this.authService.isAuthenticated()) {
      this.router.navigate(['/login']);
    }
  }
}
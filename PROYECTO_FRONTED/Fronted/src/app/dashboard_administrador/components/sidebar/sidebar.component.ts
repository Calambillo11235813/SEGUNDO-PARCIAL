import { Component, Input } from '@angular/core';
import { RouterModule } from '@angular/router';
import { CommonModule } from '@angular/common';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-sidebar',
  templateUrl: './sidebar.component.html',
  styleUrls: ['./sidebar.component.css'],
  standalone: true,
  imports: [CommonModule, RouterModule]
})
export class SidebarComponent {
  @Input() isAdmin = false;

  constructor(private authService: AuthService) {
    console.log('SidebarComponent inicializado, isAdmin:', this.isAdmin); // Para debugging
  }

  ngOnChanges() {
    console.log('SidebarComponent isAdmin cambió a:', this.isAdmin); // Para debugging
  }
  
  logout(): void {
    this.authService.logout();
    window.location.href = '/login';
  }
}
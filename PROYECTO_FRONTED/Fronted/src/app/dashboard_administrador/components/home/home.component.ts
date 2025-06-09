import { Component, OnInit } from '@angular/core';
import { AuthService } from '../../../services/auth.service';
import { CommonModule } from '@angular/common'; // ✅ AGREGAR ESTA IMPORTACIÓN
import { RouterModule } from '@angular/router';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  standalone: true,
  imports: [CommonModule, RouterModule], // ✅ AGREGAR CommonModule
})
export class HomeComponent implements OnInit {
  usuario: any;
  
  constructor(private authService: AuthService) {}
  
  ngOnInit(): void {
    this.usuario = this.authService.getCurrentUser();
  }
}
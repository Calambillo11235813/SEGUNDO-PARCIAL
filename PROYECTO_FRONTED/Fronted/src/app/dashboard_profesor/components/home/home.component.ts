import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule } from '@angular/router';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-home-profesor',
  templateUrl: './home.component.html',
  standalone: true,
  imports: [CommonModule,RouterModule]
})
export class HomeProfesorComponent implements OnInit {
  usuario: any;
  
  constructor(private authService: AuthService) {}
  
  ngOnInit(): void {
    this.usuario = this.authService.getCurrentUser();
  }
}
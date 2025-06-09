import { Component, OnInit } from '@angular/core';
import { UsuarioService } from '../../../services/home.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  standalone: true,
  imports: [],
})
export class HomeComponent implements OnInit {
  cantidadEstudiantes: number = 0;
  cantidadProfesores: number = 0;

  constructor(private usuarioService: UsuarioService) {}

  ngOnInit(): void {
    this.usuarioService.getCantidadEstudiantes().subscribe((data) => {
      this.cantidadEstudiantes = data.total;
    });

    this.usuarioService.getCantidadProfesores().subscribe((data) => {
      this.cantidadProfesores = data.total;
    });
  }
}
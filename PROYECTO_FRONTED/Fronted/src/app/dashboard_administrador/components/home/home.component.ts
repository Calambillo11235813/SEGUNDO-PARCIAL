import { Component, OnInit } from '@angular/core';
import { RouterModule } from '@angular/router';
import { UsuarioService } from '../../../services/home.service';

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  standalone: true,
  imports: [RouterModule],
})
export class HomeComponent implements OnInit {
  cantidadEstudiantes: number = 0;
  cantidadProfesores: number = 0;
  cantidadCursos: number = 0;
  cantidadMaterias: number = 0;

  constructor(private usuarioService: UsuarioService) {}

  ngOnInit(): void {
    this.usuarioService.getCantidadEstudiantes().subscribe((data) => {
      this.cantidadEstudiantes = data.total;
    });

    this.usuarioService.getCantidadProfesores().subscribe((data) => {
      this.cantidadProfesores = data.total;
    });

    this.usuarioService.getCantidadCursos().subscribe((data) => {
      this.cantidadCursos = data.cantidad_cursos;
    });

    this.usuarioService.getCantidadMaterias().subscribe((data) => {
      this.cantidadMaterias = data.cantidad_materias;
    });
  }
}
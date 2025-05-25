import { Routes } from '@angular/router';
import { LoginComponent } from './auth/components/login/login.component';
import { DashboardComponent } from './dashboard_administrador/dashboard.component';
import { HomeComponent } from './dashboard_administrador/components/home/home.component';
import { EstudiantesComponent } from './dashboard_administrador/components/estudiantes/estudiantes.component';
import { ProfesoresComponent } from './dashboard_administrador/components/profesores/profesores.component';
import { PerfilComponent } from './dashboard_administrador/components/perfil/perfil.component';
import { CursosComponent } from './dashboard_administrador/components/cursos/cursos.component';
import { MateriasComponent } from './dashboard_administrador/components/materias/materias.component';
import { AuthGuard } from './core/guards/auth.guard';
import { AdminGuard } from './core/guards/admin.guard';
import { TeacherGuard } from './core/guards/teacher.guard'; // Importar TeacherGuard
import { DashboardProfesorComponent } from './dashboard_profesor/dashboard.component';
import { HomeProfesorComponent } from './dashboard_profesor/components/home/home.component';
import { MateriasProfesorComponent } from './dashboard_profesor/components/materias/materias.component';
import { AsistenciasComponent } from './dashboard_profesor/components/asistencias/asistencias.component';
import { NotasComponent } from './dashboard_profesor/components/notas/notas.component';
import { PerfilProfesorComponent } from './dashboard_profesor/components/perfil/perfil.component'; // Importar PerfilProfesorComponent

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard],
    children: [
      { path: '', component: HomeComponent },
      { path: 'estudiantes', component: EstudiantesComponent, canActivate: [AdminGuard] },
      { path: 'profesores', component: ProfesoresComponent, canActivate: [AdminGuard] },
      { path: 'cursos', component: CursosComponent, canActivate: [AdminGuard] },
      { path: 'materias', component: MateriasComponent, canActivate: [AdminGuard] },
      { path: 'perfil', component: PerfilComponent }
    ]
  },
  // Rutas para el dashboard de profesor
  {
    path: 'profesor',
    component: DashboardProfesorComponent,
    canActivate: [AuthGuard, TeacherGuard], // Añadir TeacherGuard
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: HomeProfesorComponent },
      { path: 'materias', component: MateriasProfesorComponent },
      { path: 'asistencias', component: AsistenciasComponent },
      { path: 'notas', component: NotasComponent },
      { path: 'perfil', component: PerfilProfesorComponent } // Añadir ruta de perfil
    ]
  }
];

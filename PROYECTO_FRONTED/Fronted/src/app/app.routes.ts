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
import { TeacherGuard } from './core/guards/teacher.guard';
import { DashboardProfesorComponent } from './dashboard_profesor/dashboard.component';
import { HomeProfesorComponent } from './dashboard_profesor/components/home/home.component';
import { MateriasProfesorComponent } from './dashboard_profesor/components/materias/materias.component';
import { AsistenciasComponent } from './dashboard_profesor/components/asistencias/asistencias.component';
import { NotasComponent } from './dashboard_profesor/components/notas/notas.component';
import { PerfilProfesorComponent } from './dashboard_profesor/components/perfil/perfil.component';
import { DetalleMateriaComponent } from './dashboard_profesor/components/materias/materia_detalle.component';
import { ListaAsistenciasComponent } from './dashboard_profesor/components/asistencias/lista-asistencias.component';

export const routes: Routes = [
  { path: '', redirectTo: '/login', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  
  // ✅ Rutas principales de administrador
  {
    path: 'admin',
    component: DashboardComponent,
    canActivate: [AuthGuard, AdminGuard],
    children: [
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      { path: 'home', component: HomeComponent },
      { path: 'estudiantes', component: EstudiantesComponent },
      { path: 'profesores', component: ProfesoresComponent },
      { path: 'cursos', component: CursosComponent },
      { path: 'materias', component: MateriasComponent },
      { path: 'perfil', component: PerfilComponent }
    ]
  },
  
  // ✅ Rutas de profesor
  {
    path: 'profesor',
    component: DashboardProfesorComponent,
    canActivate: [AuthGuard, TeacherGuard],
    children: [
      { path: '', redirectTo: 'home', pathMatch: 'full' },
      { path: 'home', component: HomeProfesorComponent },
      { path: 'materias', component: MateriasProfesorComponent },
      { path: 'materia/:id', component: DetalleMateriaComponent },
      { path: 'asistencias', component: AsistenciasComponent },
      { path: 'lista-asistencias', component: ListaAsistenciasComponent },
      { path: 'notas', component: NotasComponent },
      { path: 'perfil', component: PerfilProfesorComponent }
    ]
  }
];

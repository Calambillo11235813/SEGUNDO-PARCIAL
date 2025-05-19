import { Routes } from '@angular/router';
import { LoginComponent } from './auth/components/login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { HomeComponent } from './dashboard/components/home/home.component';
import { EstudiantesComponent } from './dashboard/components/estudiantes/estudiantes.component';
import { ProfesoresComponent } from './dashboard/components/profesores/profesores.component';
import { PerfilComponent } from './dashboard/components/perfil/perfil.component';
import { AuthGuard } from './core/guards/auth.guard';
import { AdminGuard } from './core/guards/admin.guard';

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
      { path: 'perfil', component: PerfilComponent }
    ]
  }
];

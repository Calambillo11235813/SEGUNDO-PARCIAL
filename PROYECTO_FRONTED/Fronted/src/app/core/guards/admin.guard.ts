import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

export const AdminGuard: CanActivateFn = (route, state) => {
  const authService = inject(AuthService);
  const router = inject(Router);
  
  const usuario = authService.getCurrentUser();
  
  if (usuario?.rol?.nombre === 'Administrador') {
    return true;
  }
  
  router.navigate(['/dashboard']);
  return false;
};
import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { LoginComponent } from './components/login/login.component';

@NgModule({
  declarations: [
    // Quitar LoginComponent de aquí
  ],
  imports: [
    CommonModule,
    ReactiveFormsModule,
    RouterModule,
    LoginComponent // Importarlo aquí en su lugar
  ],
  exports: [
    LoginComponent
  ]
})
export class AuthModule { }

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';
import { AsistenciasService } from '../../../services/asistencias.service';

// ✅ Definir interfaces para tipado correcto
interface Materia {
  id: number;
  nombre: string;
  curso?: {
    id: number;
    nivel?: { id: number; nombre: string };
    grado: number;
    paralelo: string;
  };
  curso_nombre?: string;
  estudiantes_count?: number;
}

interface MateriasResponse {
  materias?: Materia[];
  data?: Materia[];
  [key: string]: any;
}

@Component({
  selector: 'app-asistencias',
  templateUrl: './asistencias.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class AsistenciasComponent implements OnInit {
  materias: Materia[] = [];           // ✅ Tipado correcto
  estudiantes: any[] = [];
  asistenciaForm: FormGroup;
  loading = false;
  materiasLoading = false;
  estudiantesLoading = false;
  error = '';
  mensaje = '';
  
  // Nuevas propiedades para mejorar UX
  guardandoAsistencias = false;
  mostrarConfirmacion = false;
  resumenAsistencias: any = null;
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private materiasService: MateriasService,
    private asistenciasService: AsistenciasService
  ) {
    this.asistenciaForm = this.fb.group({
      materia: [null, Validators.required],
      fecha: [this.obtenerFechaActual(), Validators.required]
    });
  }
  
  ngOnInit(): void {
    this.cargarMaterias();
    
    // Escuchar cambios en el formulario para cargar estudiantes
    this.asistenciaForm.get('materia')?.valueChanges.subscribe(value => {
      if (value) {
        this.cargarEstudiantes();
      }
    });
  }
  
  obtenerFechaActual(): string {
    const hoy = new Date();
    const año = hoy.getFullYear();
    const mes = String(hoy.getMonth() + 1).padStart(2, '0');
    const dia = String(hoy.getDate()).padStart(2, '0');
    return `${año}-${mes}-${dia}`;
  }
  
  cargarMaterias(): void {
    this.materiasLoading = true;
    this.error = '';
    
    const usuario = this.authService.getCurrentUser();
    
    if (usuario && usuario.id) {
      this.materiasService.getMateriasPorProfesor(usuario.id).subscribe({
        next: (response: any) => {  // ✅ Tipado como any para manejar diferentes formatos
          console.log('Respuesta materias:', response);
          
          // ✅ Verificar si la respuesta es un array o un objeto con tipado seguro
          if (Array.isArray(response)) {
            this.materias = response as Materia[];
          } else if (response && typeof response === 'object') {
            const data = response as MateriasResponse;
            if (data.materias && Array.isArray(data.materias)) {
              this.materias = data.materias;
            } else if (data.data && Array.isArray(data.data)) {
              this.materias = data.data;
            } else {
              // Si el objeto tiene propiedades numericas (como un objeto indexado)
              const values = Object.values(response);
              if (values.length > 0 && typeof values[0] === 'object') {
                this.materias = values as Materia[];
              } else {
                this.materias = [];
              }
            }
          } else {
            console.warn('Respuesta inesperada:', response);
            this.materias = [];
          }
          
          this.materiasLoading = false;
          
          if (this.materias.length === 0) {
            this.error = 'No tienes materias asignadas';
          }
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar materias. Intenta nuevamente.';
          this.materiasLoading = false;
          
          // Fallback a datos simulados en caso de error
          this.cargarMateriasSimuladas();
        }
      });
    } else {
      this.materiasLoading = false;
      this.error = 'No se pudo identificar al profesor';
    }
  }
  
  cargarMateriasSimuladas(): void {
    // Datos simulados como fallback
    setTimeout(() => {
      this.materias = [
        {
          id: 1,
          nombre: 'Matemáticas',
          curso: {
            id: 101,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 8,
            paralelo: 'A'
          },
          curso_nombre: 'Octavo A - Básica',
          estudiantes_count: 32
        },
        {
          id: 2,
          nombre: 'Lenguaje y Literatura',
          curso: {
            id: 101,
            nivel: { id: 1, nombre: 'Educación Básica' },
            grado: 8,
            paralelo: 'A'
          },
          curso_nombre: 'Octavo A - Básica',
          estudiantes_count: 32
        }
      ];
      this.materiasLoading = false;
    }, 500);
  }
  
  cargarEstudiantes(): void {
    const materiaId = this.asistenciaForm.get('materia')?.value;
    if (!materiaId) return;
    
    this.estudiantesLoading = true;
    this.estudiantes = [];
    this.error = '';
    this.mensaje = '';
    
    this.asistenciasService.getEstudiantesPorMateria(materiaId).subscribe({
      next: (response: any) => {  // ✅ Tipado como any para flexibilidad
        console.log('Respuesta estudiantes:', response);
        
        let estudiantesData: any[] = [];
        
        if (Array.isArray(response)) {
          estudiantesData = response;
        } else if (response && response.estudiantes && Array.isArray(response.estudiantes)) {
          estudiantesData = response.estudiantes;
        } else if (response && response.data && Array.isArray(response.data)) {
          estudiantesData = response.data;
        } else {
          console.warn('Formato de respuesta inesperado:', response);
          estudiantesData = [];
        }
        
        if (estudiantesData.length > 0) {
          this.estudiantes = estudiantesData.map((est: any) => ({
            ...est,
            asistio: true,
            justificada: false
          }));
        } else {
          this.error = response?.advertencia || response?.mensaje || 'No hay estudiantes asignados a esta materia';
        }
        
        this.estudiantesLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes:', error);
        this.error = 'Error al cargar los estudiantes. Verifica la conexión.';
        this.estudiantesLoading = false;
        
        // Fallback a datos simulados
        this.cargarEstudiantesSimulados(materiaId);
      }
    });
  }
  
  cargarEstudiantesSimulados(materiaId: number): void {
    this.estudiantes = [];
    
    setTimeout(() => {
      const cantidadEstudiantes = 20 + (materiaId % 5);
      
      for (let i = 1; i <= cantidadEstudiantes; i++) {
        this.estudiantes.push({
          id: i,
          nombre: `Nombre ${i}`,
          apellido: `Apellido ${i}`,
          codigo: `EST${1000 + i}`,
          asistio: true,
          justificada: false
        });
      }
      
      this.estudiantesLoading = false;
    }, 500);
  }
  
  toggleAsistencia(estudiante: any): void {
    estudiante.asistio = !estudiante.asistio;
    
    if (!estudiante.asistio) {
      estudiante.justificada = false;
    } else {
      estudiante.justificada = false;
    }
  }
  
  toggleJustificacion(estudiante: any): void {
    if (!estudiante.asistio) {
      estudiante.justificada = !estudiante.justificada;
    }
  }
  
  obtenerResumenAsistencias(): any {
    const total = this.estudiantes.length;
    const presentes = this.estudiantes.filter(est => est.asistio).length;
    const ausentes = this.estudiantes.filter(est => !est.asistio).length;
    const justificadas = this.estudiantes.filter(est => !est.asistio && est.justificada).length;
    const injustificadas = ausentes - justificadas;
    
    return {
      total,
      presentes,
      ausentes,
      justificadas,
      injustificadas,
      porcentajeAsistencia: total > 0 ? Math.round((presentes / total) * 100) : 0
    };
  }
  
  mostrarConfirmacionGuardado(): void {
    if (this.asistenciaForm.invalid || this.estudiantes.length === 0) {
      return;
    }
    
    this.resumenAsistencias = this.obtenerResumenAsistencias();
    this.mostrarConfirmacion = true;
  }
  
  cancelarGuardado(): void {
    this.mostrarConfirmacion = false;
    this.resumenAsistencias = null;
  }
  
  confirmarGuardado(): void {
    this.mostrarConfirmacion = false;
    this.guardarAsistencias();
  }
  
  guardarAsistencias(): void {
    if (this.asistenciaForm.invalid || this.estudiantes.length === 0) {
      return;
    }
    
    this.guardandoAsistencias = true;
    this.mensaje = '';
    this.error = '';
    
    const asistenciasData = {
      materia_id: this.asistenciaForm.get('materia')?.value,
      fecha: this.asistenciaForm.get('fecha')?.value,
      asistencias: this.estudiantes.map(est => ({
        estudiante_id: est.id,
        presente: est.asistio,
        justificada: est.justificada
      }))
    };
    
    this.asistenciasService.registrarAsistenciasMasivo(asistenciasData).subscribe({
      next: (response: any) => {
        console.log('Respuesta del servidor:', response);
        
        const errores = response.resultados?.filter((r: any) => !r.success) || [];
        const exitosos = response.resultados?.filter((r: any) => r.success) || [];
        
        if (errores.length === 0) {
          this.mensaje = `✅ Asistencias registradas correctamente para ${exitosos.length} estudiantes`;
        } else if (exitosos.length > 0) {
          this.mensaje = `⚠️ Asistencias registradas para ${exitosos.length} estudiantes. ${errores.length} con errores.`;
          this.error = `Errores: ${errores.map((e: any) => e.error).join(', ')}`;
        } else {
          this.error = `❌ Error al registrar asistencias: ${errores.map((e: any) => e.error).join(', ')}`;
        }
        
        this.guardandoAsistencias = false;
        
        setTimeout(() => {
          this.mensaje = '';
          this.error = '';
        }, 5000);
      },
      error: (error) => {
        console.error('Error al guardar asistencias:', error);
        this.error = 'Error al guardar las asistencias. Verifica la conexión e intenta nuevamente.';
        this.guardandoAsistencias = false;
        
        setTimeout(() => {
          this.error = '';
        }, 5000);
      }
    });
  }
  
  marcarTodosPresentes(): void {
    this.estudiantes.forEach(est => {
      est.asistio = true;
      est.justificada = false;
    });
  }
  
  marcarTodosAusentes(): void {
    this.estudiantes.forEach(est => {
      est.asistio = false;
      est.justificada = false;
    });
  }
  
  getMateriaSeleccionada(): Materia | undefined {  // ✅ Tipado correcto del retorno
    const materiaId = this.asistenciaForm.get('materia')?.value;
    return this.materias.find(m => m.id == materiaId);
  }
}
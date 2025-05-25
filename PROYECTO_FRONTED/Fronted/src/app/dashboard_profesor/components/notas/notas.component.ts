import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import { AuthService } from '../../../services/auth.service';
import { MateriasService } from '../../../services/materias.service';

@Component({
  selector: 'app-notas',
  templateUrl: './notas.component.html',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule]
})
export class NotasComponent implements OnInit {
  materias: any[] = [];
  estudiantes: any[] = [];
  notasForm: FormGroup;
  loading = false;
  materiasLoading = false;
  estudiantesLoading = false;
  error = '';
  mensaje = '';
  
  constructor(
    private fb: FormBuilder,
    private authService: AuthService,
    private materiasService: MateriasService
  ) {
    this.notasForm = this.fb.group({
      materia: [null, Validators.required],
      parcial: ['1', Validators.required]
    });
  }
  
  ngOnInit(): void {
    this.cargarMaterias();
    
    // Escuchar cambios en el formulario para cargar estudiantes
    this.notasForm.valueChanges.subscribe(values => {
      if (values.materia && values.parcial) {
        this.cargarEstudiantes();
      }
    });
  }
  
  cargarMaterias(): void {
    this.materiasLoading = true;
    
    // Comentar la llamada al API real
    /*
    const usuario = this.authService.getCurrentUser();
    
    if (usuario && usuario.id) {
      this.materiasService.getMateriasPorProfesor(usuario.id).subscribe({
        next: (data) => {
          this.materias = data;
          this.materiasLoading = false;
        },
        error: (error) => {
          console.error('Error al cargar materias:', error);
          this.error = 'Error al cargar materias';
          this.materiasLoading = false;
        }
      });
    } else {
      this.materiasLoading = false;
      this.error = 'No se pudo identificar al profesor';
    }
    */
    
    // Simular datos de materias para prueba
    setTimeout(() => {
      this.materias = [
        { id: 1, nombre: 'Matemáticas', curso: { nivel: { nombre: 'Básica' }, grado: 8, paralelo: 'A' } },
        { id: 2, nombre: 'Lenguaje', curso: { nivel: { nombre: 'Básica' }, grado: 8, paralelo: 'A' } },
        { id: 3, nombre: 'Ciencias Naturales', curso: { nivel: { nombre: 'Básica' }, grado: 7, paralelo: 'B' } },
        { id: 4, nombre: 'Historia', curso: { nivel: { nombre: 'Básica' }, grado: 7, paralelo: 'B' } }
      ];
      this.materiasLoading = false;
    }, 800);
  }
  
  cargarEstudiantes(): void {
    const materiaId = this.notasForm.get('materia')?.value;
    const parcial = this.notasForm.get('parcial')?.value;
    
    if (!materiaId || !parcial) return;
    
    this.estudiantesLoading = true;
    this.estudiantes = [];
    
    // Comentar la llamada al API real
    /*
    this.materiasService.getEstudiantesConNotasPorMateria(materiaId, parcial).subscribe({
      next: (data) => {
        this.estudiantes = data.map((est: any) => ({
          ...est,
          nota: est.nota || 0 // Si no tiene nota, inicializar en 0
        }));
        this.estudiantesLoading = false;
      },
      error: (error) => {
        console.error('Error al cargar estudiantes:', error);
        this.error = 'Error al cargar los estudiantes';
        this.estudiantesLoading = false;
      }
    });
    */
    
    // Simular datos de estudiantes para prueba
    setTimeout(() => {
      // Generar estudiantes diferentes según la materia seleccionada
      const numEstudiantes = 10 + (materiaId % 5); // Variar cantidad según materia
      this.estudiantes = [];
      
      for (let i = 1; i <= numEstudiantes; i++) {
        this.estudiantes.push({
          id: i,
          nombre: `Nombre ${i}`,
          apellido: `Apellido ${i}`,
          codigo: `EST-${1000 + i}`,
          nota: parcial === '1' ? (Math.random() * 10).toFixed(2) : (Math.random() * 10).toFixed(2)
        });
      }
      
      this.estudiantesLoading = false;
    }, 800);
  }
  
  cambiarNota(estudiante: any, evento: any): void {
    let valor = parseFloat(evento.target.value);
    
    // Validar que la nota esté entre 0 y 10
    if (isNaN(valor)) valor = 0;
    if (valor < 0) valor = 0;
    if (valor > 10) valor = 10;
    
    estudiante.nota = valor;
  }
  
  guardarNotas(): void {
    if (this.notasForm.invalid || this.estudiantes.length === 0) {
      return;
    }
    
    this.loading = true;
    this.mensaje = '';
    this.error = '';
    
    const notasData = {
      materia_id: this.notasForm.get('materia')?.value,
      parcial: this.notasForm.get('parcial')?.value,
      notas: this.estudiantes.map(est => ({
        estudiante_id: est.id,
        nota: est.nota
      }))
    };
    
    // La llamada al API está comentada
    /*
    this.notasService.guardarNotas(notasData).subscribe({
      next: () => {
        this.mensaje = 'Calificaciones registradas correctamente';
        this.loading = false;
      },
      error: (error) => {
        console.error('Error al guardar calificaciones:', error);
        this.error = 'Error al guardar las calificaciones';
        this.loading = false;
      }
    });
    */
    
    // Simulación para prueba
    setTimeout(() => {
      this.mensaje = 'Calificaciones registradas correctamente';
      this.loading = false;
    }, 1000);
  }
}
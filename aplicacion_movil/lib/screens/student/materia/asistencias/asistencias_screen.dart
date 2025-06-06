import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../../../models/usuario.dart';
import '../../../../services/auth_service.dart';
import '../../../../services/estudiante/asistencias_service.dart';
import '../../../../widgets/student_drawer.dart';

class AsistenciasScreen extends StatefulWidget {
  final String? filtroMateriaId;
  final String? nombreMateria;

  const AsistenciasScreen({
    super.key,
    this.filtroMateriaId,
    this.nombreMateria,
  });

  @override
  State<AsistenciasScreen> createState() => _AsistenciasScreenState();
}

class _AsistenciasScreenState extends State<AsistenciasScreen> {
  bool isLoading = true;
  List<dynamic> asistencias = [];
  String? errorMessage;
  Usuario? currentUser;
  String? selectedMateriaId;

  // Para filtros
  List<Map<String, dynamic>> materias = [];
  DateTime? fechaInicio;
  DateTime? fechaFin;

  @override
  void initState() {
    super.initState();
    // Si viene con filtro de materia preestablecido
    if (widget.filtroMateriaId != null) {
      selectedMateriaId = widget.filtroMateriaId;
    }
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      // Obtener usuario actual
      final user = await AuthService.getCurrentUser();

      if (user == null) {
        setState(() {
          isLoading = false;
          errorMessage = 'No se pudo obtener la información del usuario';
        });
        return;
      }

      setState(() {
        currentUser = user;
      });

      // Formatear fechas si existen
      String? fechaInicioStr;
      String? fechaFinStr;

      if (fechaInicio != null) {
        fechaInicioStr = DateFormat('yyyy-MM-dd').format(fechaInicio!);
      }

      if (fechaFin != null) {
        fechaFinStr = DateFormat('yyyy-MM-dd').format(fechaFin!);
      }

      // Cargar asistencias
      final data = await AsistenciasService.obtenerAsistenciasPorEstudiante(
        user.id.toString(),
        materiaId: selectedMateriaId,
        fechaInicio: fechaInicioStr,
        fechaFin: fechaFinStr,
      );

      // Extraer lista de materias para el filtro
      final materiasLista = <Map<String, dynamic>>[];

      for (var asistencia in data) {
        materiasLista.add({
          'id': asistencia['id'].toString(),
          'nombre': asistencia['nombre'],
        });
      }

      setState(() {
        asistencias = data;
        materias = materiasLista;
        isLoading = false;
      });
    } catch (e) {
      setState(() {
        isLoading = false;
        errorMessage = 'Error al cargar las asistencias: $e';
      });
    }
  }

  Future<void> _filtrarPorMateria(String? materiaId) async {
    setState(() {
      isLoading = true;
      selectedMateriaId = materiaId;
    });

    await _loadData();
  }

  Future<void> _filtrarPorFecha(DateTime? inicio, DateTime? fin) async {
    setState(() {
      isLoading = true;
      fechaInicio = inicio;
      fechaFin = fin;
    });

    await _loadData();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          widget.nombreMateria != null
              ? 'Asistencia: ${widget.nombreMateria}'
              : 'Mi Asistencia',
        ),
        actions: [
          // Añadir el botón de registro en la AppBar si hay una materia seleccionada
          if (widget.filtroMateriaId != null)
            IconButton(
              icon: const Icon(Icons.add_circle),
              tooltip: 'Registrar asistencia',
              onPressed: () {
                Navigator.pushNamed(
                  context,
                  '/student/materia/registrar-asistencia',
                  arguments: {
                    'materia': {
                      'id': widget.filtroMateriaId,
                      'nombre': widget.nombreMateria,
                    },
                  },
                );
              },
            ),
          IconButton(
            icon: const Icon(Icons.filter_list),
            onPressed: () {
              _showFilterDialog(context);
            },
          ),
          IconButton(
            icon: const Icon(Icons.date_range),
            onPressed: () {
              _showDateFilterDialog(context);
            },
          ),
        ],
      ),
      drawer:
          currentUser != null
              ? StudentDrawer(
                currentUser: currentUser,
                currentRoute: '/student/asistencias',
              )
              : null,
      body:
          isLoading
              ? const Center(child: CircularProgressIndicator())
              : errorMessage != null
              ? Center(child: Text(errorMessage!))
              : _buildAsistenciasList(),
    );
  }

  void _showFilterDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Filtrar por materia'),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView(
              shrinkWrap: true,
              children: [
                ListTile(
                  title: const Text('Todas las materias'),
                  selected: selectedMateriaId == null,
                  onTap: () {
                    Navigator.pop(context);
                    _filtrarPorMateria(null);
                  },
                ),
                ...materias.map(
                  (materia) => ListTile(
                    title: Text(materia['nombre']),
                    selected: selectedMateriaId == materia['id'],
                    onTap: () {
                      Navigator.pop(context);
                      _filtrarPorMateria(materia['id']);
                    },
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
          ],
        );
      },
    );
  }

  void _showDateFilterDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Filtrar por fechas'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                title: const Text('Fecha de inicio'),
                subtitle: Text(
                  fechaInicio != null
                      ? DateFormat('dd/MM/yyyy').format(fechaInicio!)
                      : 'No seleccionada',
                ),
                onTap: () async {
                  final fecha = await showDatePicker(
                    context: context,
                    initialDate: fechaInicio ?? DateTime.now(),
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now(),
                  );

                  if (fecha != null) {
                    setState(() {
                      fechaInicio = fecha;
                    });
                  }
                },
                trailing: const Icon(Icons.calendar_today),
              ),
              ListTile(
                title: const Text('Fecha de fin'),
                subtitle: Text(
                  fechaFin != null
                      ? DateFormat('dd/MM/yyyy').format(fechaFin!)
                      : 'No seleccionada',
                ),
                onTap: () async {
                  final fecha = await showDatePicker(
                    context: context,
                    initialDate: fechaFin ?? DateTime.now(),
                    firstDate: DateTime(2020),
                    lastDate: DateTime.now(),
                  );

                  if (fecha != null) {
                    setState(() {
                      fechaFin = fecha;
                    });
                  }
                },
                trailing: const Icon(Icons.calendar_today),
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () {
                setState(() {
                  fechaInicio = null;
                  fechaFin = null;
                });
                Navigator.pop(context);
                _filtrarPorFecha(null, null);
              },
              child: const Text('Limpiar'),
            ),
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancelar'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pop(context);
                _filtrarPorFecha(fechaInicio, fechaFin);
              },
              child: const Text('Aplicar'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildAsistenciasList() {
    if (asistencias.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text('No hay registros de asistencia disponibles'),
            const SizedBox(height: 20),
            if (widget.filtroMateriaId != null)
              ElevatedButton.icon(
                icon: const Icon(Icons.add),
                label: const Text('Registrar asistencia'),
                onPressed: () {
                  Navigator.pushNamed(
                    context,
                    '/student/materia/registrar-asistencia',
                    arguments: {
                      'materia': {
                        'id': widget.filtroMateriaId,
                        'nombre': widget.nombreMateria,
                      },
                    },
                  );
                },
              ),
          ],
        ),
      );
    }

    return ListView(
      children: [
        // Calendario al inicio
        _buildCalendario(),

        // Lista de asistencias (existente)
        ...asistencias.map((asistencia) {
          // Calcular porcentaje de asistencia para mostrar en la barra de progreso
          final porcentaje = asistencia['porcentaje_asistencia'] / 100;

          return Card(
            margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ExpansionTile(
              title: Text(
                asistencia['nombre'],
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SizedBox(height: 4),
                  LinearProgressIndicator(
                    value: porcentaje,
                    backgroundColor: Colors.grey[300],
                    color:
                        porcentaje >= 0.75
                            ? Colors.green
                            : porcentaje >= 0.6
                            ? Colors.orange
                            : Colors.red,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Asistencia: ${asistencia['asistencias']} de ${asistencia['total_clases']} clases (${asistencia['porcentaje_asistencia']}%)',
                    style: TextStyle(
                      color:
                          porcentaje >= 0.75
                              ? Colors.green
                              : porcentaje >= 0.6
                              ? Colors.orange
                              : Colors.red,
                    ),
                  ),
                ],
              ),
              children: [
                Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Detalle de asistencias:',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 8),

                      // Lista detallada de asistencias
                      ...asistencia['detalle'].map<Widget>((detalle) {
                        final fecha = DateFormat(
                          'dd/MM/yyyy',
                        ).format(DateTime.parse(detalle['fecha']));

                        return ListTile(
                          contentPadding: EdgeInsets.zero,
                          leading: Icon(
                            detalle['presente']
                                ? Icons.check_circle
                                : detalle['justificada']
                                ? Icons.outlined_flag
                                : Icons.cancel,
                            color:
                                detalle['presente']
                                    ? Colors.green
                                    : detalle['justificada']
                                    ? Colors.amber
                                    : Colors.red,
                          ),
                          title: Text(fecha),
                          subtitle: Text(
                            detalle['presente']
                                ? 'Presente'
                                : detalle['justificada']
                                ? 'Falta justificada'
                                : 'Falta sin justificación',
                          ),
                        );
                      }),
                    ],
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }

  Widget _buildCalendario() {
    // Colores para los diferentes estados
    final colorPresente = Color(
      0xFFFFB74D,
    ); // Color amarillo/naranja para presente
    final colorAusente = Colors.red[100]!; // Rojo claro para ausente
    final colorJustificado = Colors.blue[100]!; // Azul claro para justificado

    // Variables para el calendario
    final focusedDay = DateTime.now();
    final firstDay = DateTime(DateTime.now().year - 1, 1, 1);
    final lastDay = DateTime(DateTime.now().year + 1, 12, 31);

    // Preparar datos de asistencia más sofisticados para el calendario
    Map<String, Map<String, dynamic>> asistenciasPorFecha = {};

    for (var asistencia in asistencias) {
      if (asistencia['detalle'] != null) {
        for (var detalle in asistencia['detalle']) {
          if (detalle['fecha'] != null) {
            try {
              final fechaStr = detalle['fecha'].toString();
              final fechaKey = fechaStr.split('T')[0]; // Formato YYYY-MM-DD

              asistenciasPorFecha[fechaKey] = {
                'presente': detalle['presente'] ?? false,
                'justificada': detalle['justificada'] ?? false,
                'materia': asistencia['nombre'],
              };
            } catch (e) {
              debugPrint('Error al procesar fecha: ${detalle['fecha']}');
            }
          }
        }
      }
    }

    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Calendario de Clases',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            TableCalendar(
              firstDay: firstDay,
              lastDay: lastDay,
              focusedDay: focusedDay,
              currentDay: DateTime.now(),
              calendarFormat: CalendarFormat.month,
              availableCalendarFormats: const {
                CalendarFormat.month: 'Mes',
                CalendarFormat.twoWeeks: '2 semanas',
                CalendarFormat.week: 'Semana',
              },
              calendarStyle: CalendarStyle(
                weekendTextStyle: TextStyle(color: Colors.red),
              ),
              calendarBuilders: CalendarBuilders(
                defaultBuilder: (context, day, focusedDay) {
                  final fechaKey =
                      "${day.year}-${day.month.toString().padLeft(2, '0')}-${day.day.toString().padLeft(2, '0')}";
                  final asistencia = asistenciasPorFecha[fechaKey];

                  if (asistencia != null) {
                    // Determinar el color basado en el estado de asistencia
                    Color bgColor;
                    if (asistencia['presente'] == true) {
                      bgColor = colorPresente;
                    } else if (asistencia['justificada'] == true) {
                      bgColor = colorJustificado;
                    } else {
                      bgColor = colorAusente;
                    }

                    return Container(
                      decoration: BoxDecoration(
                        color: bgColor,
                        shape: BoxShape.circle,
                      ),
                      margin: const EdgeInsets.all(4.0),
                      alignment: Alignment.center,
                      child: Text(
                        day.day.toString(),
                        style: TextStyle(
                          color:
                              asistencia['presente']
                                  ? Colors.white
                                  : Colors.black87,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    );
                  }
                  return null; // Usar el estilo predeterminado
                },
              ),
            ),

            // 3. Añadir una leyenda para explicar los colores
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildLeyendaItem('Presente', colorPresente),
                const SizedBox(width: 16),
                _buildLeyendaItem('Ausente', colorAusente),
                const SizedBox(width: 16),
                _buildLeyendaItem('Justificada', colorJustificado),
              ],
            ),
          ],
        ),
      ),
    );
  }

  // Ayuda para construir un elemento de leyenda
  Widget _buildLeyendaItem(String label, Color color) {
    return Row(
      children: [
        Container(
          width: 16,
          height: 16,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
        ),
        const SizedBox(width: 4),
        Text(label, style: TextStyle(fontSize: 12)),
      ],
    );
  }
}

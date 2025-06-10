import 'package:flutter/material.dart';
import 'package:aplicacion_movil/config/theme_config.dart';

class DashboardAppBar extends StatelessWidget implements PreferredSizeWidget {
  final String title;
  final String subtitle;
  final VoidCallback? onRefresh;
  final List<Widget>? actions;

  const DashboardAppBar({
    super.key,
    required this.title,
    required this.subtitle,
    this.onRefresh,
    this.actions,
  });

  @override
  Widget build(BuildContext context) {
    return AppBar(
      title: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            title,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          Text(
            subtitle,
            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.normal),
          ),
        ],
      ),
      actions: [
        if (onRefresh != null)
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: onRefresh,
            tooltip: 'Actualizar',
          ),
        ...?actions,
      ],
      elevation: 4,
      backgroundColor: AppTheme.primaryColor,
    );
  }

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);
}

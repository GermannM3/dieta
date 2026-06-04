import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class AppCard extends StatelessWidget {
  const AppCard({
    super.key,
    required this.child,
    this.padding = const EdgeInsets.all(16),
    this.gradient = false,
  });

  final Widget child;
  final EdgeInsets padding;
  final bool gradient;

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: gradient ? AppTheme.cardGradient : null,
      child: Card(
        elevation: gradient ? 0 : 2,
        color: gradient ? Colors.transparent : null,
        margin: EdgeInsets.zero,
        child: Padding(padding: padding, child: child),
      ),
    );
  }
}

class SectionTitle extends StatelessWidget {
  const SectionTitle(this.title, {super.key, this.icon});

  final String title;
  final IconData? icon;

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        if (icon != null) ...[
          Icon(icon, color: AppColors.primary, size: 22),
          const SizedBox(width: 8),
        ],
        Text(
          title,
          style: const TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.w600,
            color: AppColors.foreground,
          ),
        ),
      ],
    );
  }
}

class CalorieRing extends StatelessWidget {
  const CalorieRing({
    super.key,
    required this.consumed,
    required this.target,
  });

  final double consumed;
  final double target;

  @override
  Widget build(BuildContext context) {
    final progress = target > 0 ? (consumed / target).clamp(0.0, 1.5) : 0.0;
    final remaining = target - consumed;
    Color statusColor = AppColors.healthSuccess;
    String status = 'В норме';
    if (progress > 1.0) {
      statusColor = AppColors.healthDanger;
      status = 'Превышение';
    } else if (progress > 0.85) {
      statusColor = AppColors.healthWarning;
      status = 'Почти лимит';
    }

    return Column(
      children: [
        SizedBox(
          width: 120,
          height: 120,
          child: Stack(
            alignment: Alignment.center,
            children: [
              CircularProgressIndicator(
                value: progress.clamp(0.0, 1.0),
                strokeWidth: 10,
                backgroundColor: AppColors.muted,
                color: statusColor,
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    consumed.toStringAsFixed(0),
                    style: const TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: AppColors.foreground,
                    ),
                  ),
                  Text(
                    'из ${target.toStringAsFixed(0)}',
                    style: const TextStyle(
                      fontSize: 12,
                      color: AppColors.mutedForeground,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 8),
        Container(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.15),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Text(status, style: TextStyle(color: statusColor, fontSize: 13)),
        ),
        const SizedBox(height: 4),
        Text(
          remaining >= 0
              ? 'Осталось ${remaining.toStringAsFixed(0)} ккал'
              : 'Сверх нормы на ${(-remaining).toStringAsFixed(0)} ккал',
          style: const TextStyle(color: AppColors.mutedForeground, fontSize: 13),
        ),
      ],
    );
  }
}

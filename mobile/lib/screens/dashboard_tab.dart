import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';

class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final profile = state.profile;
    final stats = state.todayStats;
    final consumed = (stats?['total_calories'] as num?)?.toDouble() ?? 0;
    final target = profile?.dailyTarget ?? 2000;
    final water = profile?.waterMl ?? 0;
    final waterTarget = profile?.waterTarget ?? 2000;

    return RefreshIndicator(
      onRefresh: state.refreshData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (state.user != null)
            Text(
              'Привет, ${profile?.name ?? state.user!.name ?? state.user!.email}! 👋',
              style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
            ),
          if (state.journey != null && state.journey!.cards.isNotEmpty) ...[
            const SizedBox(height: 12),
            _DailyMotivationBanner(card: state.journey!.cards.first),
          ],
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(
                child: AppCard(
                  gradient: true,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const SectionTitle('Калории сегодня', icon: Icons.track_changes),
                      const SizedBox(height: 16),
                      Center(child: CalorieRing(consumed: consumed, target: target)),
                    ],
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              Expanded(child: _MoodCard()),
              const SizedBox(width: 12),
              Expanded(child: _WaterCard(water: water, target: waterTarget)),
            ],
          ),
          const SizedBox(height: 16),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionTitle('БЖУ сегодня', icon: Icons.pie_chart_outline),
                const SizedBox(height: 12),
                _MacroRow('Белки', stats?['total_protein'], AppColors.accent),
                _MacroRow('Жиры', stats?['total_fat'], AppColors.healthWarning),
                _MacroRow('Углеводы', stats?['total_carbs'], AppColors.primary),
                _MacroRow('Приёмов пищи', stats?['total_meals'], AppColors.mutedForeground),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _DailyMotivationBanner extends StatelessWidget {
  const _DailyMotivationBanner({required this.card});
  final MotivationCard card;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.accent.withOpacity(0.08), AppColors.primary.withOpacity(0.08)],
        ),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.accent.withOpacity(0.2)),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(card.emoji, style: const TextStyle(fontSize: 24)),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(card.title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
                const SizedBox(height: 2),
                Text(card.text, style: const TextStyle(color: AppColors.mutedForeground, fontSize: 12, height: 1.35)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _MacroRow extends StatelessWidget {
  const _MacroRow(this.label, this.value, this.color);
  final String label;
  final dynamic value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final v = value is num ? value.toDouble() : 0.0;
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.mutedForeground)),
          Text(
            value is int ? '$value' : '${v.toStringAsFixed(1)} г',
            style: TextStyle(fontWeight: FontWeight.w600, color: color),
          ),
        ],
      ),
    );
  }
}

class _MoodCard extends StatelessWidget {
  static const moods = [
    ('excellent', '😄', 'Отлично'),
    ('good', '🙂', 'Хорошо'),
    ('okay', '😐', 'Норм'),
    ('bad', '😔', 'Плохо'),
    ('terrible', '😫', 'Ужас'),
  ];

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final current = state.profile?.mood;

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionTitle('Настроение', icon: Icons.mood),
          const SizedBox(height: 8),
          Wrap(
            spacing: 4,
            children: moods.map((m) {
              final selected = current == m.$1;
              return GestureDetector(
                onTap: () => state.setMood(m.$1),
                child: Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: selected ? AppColors.primary.withOpacity(0.15) : null,
                    borderRadius: BorderRadius.circular(8),
                    border: selected ? Border.all(color: AppColors.primary) : null,
                  ),
                  child: Text(m.$2, style: const TextStyle(fontSize: 22)),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }
}

class _WaterCard extends StatelessWidget {
  const _WaterCard({required this.water, required this.target});
  final int water;
  final int target;

  @override
  Widget build(BuildContext context) {
    final state = context.read<AppState>();
    final progress = target > 0 ? water / target : 0.0;

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionTitle('Вода', icon: Icons.water_drop),
          const SizedBox(height: 8),
          Text('$water / $target мл', style: const TextStyle(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          LinearProgressIndicator(
            value: progress.clamp(0.0, 1.0),
            backgroundColor: AppColors.muted,
            color: AppColors.accent,
            minHeight: 8,
            borderRadius: BorderRadius.circular(4),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: OutlinedButton(
                  onPressed: () => state.addWater(250),
                  style: OutlinedButton.styleFrom(minimumSize: const Size(0, 36)),
                  child: const Text('+250'),
                ),
              ),
              const SizedBox(width: 4),
              Expanded(
                child: OutlinedButton(
                  onPressed: () => state.addWater(500),
                  style: OutlinedButton.styleFrom(minimumSize: const Size(0, 36)),
                  child: const Text('+500'),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

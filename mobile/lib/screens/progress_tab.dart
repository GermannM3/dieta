import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';
import 'fat_tracker_screen.dart';

class ProgressTab extends StatelessWidget {
  const ProgressTab({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final journey = state.journey;
    final profile = state.profile;

    return RefreshIndicator(
      onRefresh: state.refreshData,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _StreakHeader(
            journeyDay: journey?.journeyDay ?? profile?.journeyDay ?? 0,
            streak: journey?.consciousStreak ?? profile?.consciousStreak ?? 0,
            longest: journey?.longestStreak ?? profile?.longestStreak ?? 0,
            totalDays: journey?.totalConsciousDays ?? profile?.totalConsciousDays ?? 0,
          ),
          const SizedBox(height: 16),
          if (journey != null && journey.cards.isNotEmpty) ...[
            const SectionTitle('Мотивация дня', icon: Icons.auto_awesome),
            const SizedBox(height: 8),
            ...journey.cards.map((c) => Padding(
                  padding: const EdgeInsets.only(bottom: 10),
                  child: _MotivationCardWidget(card: c),
                )),
            const SizedBox(height: 8),
          ],
          if (journey != null && journey.weeklyCalories.isNotEmpty) ...[
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SectionTitle('Калории за 7 дней', icon: Icons.bar_chart),
                  const SizedBox(height: 16),
                  SizedBox(
                    height: 120,
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: journey.weeklyCalories.map((d) {
                        final cal = (d['calories'] as num?)?.toDouble() ?? 0;
                        final target = profile?.dailyTarget ?? 2000;
                        final h = target > 0 ? (cal / target * 80).clamp(4.0, 80.0) : 4.0;
                        final over = cal > target * 1.1;
                        return Expanded(
                          child: Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 3),
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.end,
                              children: [
                                Text('${cal.toInt()}', style: const TextStyle(fontSize: 9, color: AppColors.mutedForeground)),
                                const SizedBox(height: 4),
                                Container(
                                  height: h,
                                  decoration: BoxDecoration(
                                    color: over ? AppColors.healthWarning : AppColors.primary,
                                    borderRadius: BorderRadius.circular(4),
                                  ),
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  (d['date'] as String).substring(5),
                                  style: const TextStyle(fontSize: 9, color: AppColors.mutedForeground),
                                ),
                              ],
                            ),
                          ),
                        );
                      }).toList(),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
          ],
          AppCard(
            gradient: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionTitle('Жировая масса', icon: Icons.monitor_weight_outlined),
                const SizedBox(height: 12),
                if (profile?.bodyFatPercent != null) ...[
                  Row(
                    children: [
                      Text(
                        '${profile!.bodyFatPercent!.toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppColors.primary),
                      ),
                      const SizedBox(width: 12),
                      if (profile.goalFatPercent != null)
                        Text('→ цель ${profile.goalFatPercent!.toStringAsFixed(1)}%',
                            style: const TextStyle(color: AppColors.mutedForeground)),
                    ],
                  ),
                  if (state.fatHistory.length >= 2) ...[
                    const SizedBox(height: 8),
                    Text(
                      _fatTrend(state.fatHistory),
                      style: const TextStyle(color: AppColors.accent, fontSize: 13),
                    ),
                  ],
                ] else
                  const Text(
                    'Сделай первый замер — талия, бёдра, (шея для мужчин). Формула Navy Method как в Telegram-боте.',
                    style: TextStyle(color: AppColors.mutedForeground, height: 1.4),
                  ),
                const SizedBox(height: 12),
                ElevatedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const FatTrackerScreen()),
                  ),
                  child: Text(profile?.bodyFatPercent != null ? 'Новый замер' : 'Начать замер'),
                ),
              ],
            ),
          ),
          const SizedBox(height: 16),
          AppCard(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionTitle('Как это работает', icon: Icons.info_outline),
                const SizedBox(height: 8),
                const Text(
                  '«Путь осознанного питания» — как в приложениях «Не курю» или «Не пью», только про еду.\n\n'
                  'Каждый день в норме калорий — +1 к серии. На экране появляются факты: что уже меняется в организме на 3-й, 7-й, 30-й день.\n\n'
                  'Не идеальность, а стабильность.',
                  style: TextStyle(color: AppColors.mutedForeground, height: 1.5, fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _fatTrend(List<Map<String, dynamic>> history) {
    if (history.length < 2) return '';
    final latest = (history.first['body_fat_percent'] as num).toDouble();
    final prev = (history[1]['body_fat_percent'] as num).toDouble();
    final diff = latest - prev;
    if (diff < -0.1) return '↓ ${(-diff).toStringAsFixed(1)} п.п. с прошлого замера';
    if (diff > 0.1) return '↑ ${diff.toStringAsFixed(1)} п.п. с прошлого замера';
    return 'Без изменений с прошлого замера';
  }
}

class _StreakHeader extends StatelessWidget {
  const _StreakHeader({
    required this.journeyDay,
    required this.streak,
    required this.longest,
    required this.totalDays,
  });

  final int journeyDay;
  final int streak;
  final int longest;
  final int totalDays;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [AppColors.primary, AppColors.primary.withOpacity(0.85)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(color: AppColors.primary.withOpacity(0.3), blurRadius: 12, offset: const Offset(0, 4)),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text('Путь осознанного питания', style: TextStyle(color: Colors.white70, fontSize: 13)),
          const SizedBox(height: 4),
          Text(
            journeyDay > 0 ? 'День $journeyDay' : 'Начни сегодня',
            style: const TextStyle(color: Colors.white, fontSize: 28, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          Row(
            children: [
              _StatChip('🔥', '$streak', 'серия'),
              const SizedBox(width: 12),
              _StatChip('🏆', '$longest', 'рекорд'),
              const SizedBox(width: 12),
              _StatChip('📅', '$totalDays', 'дней'),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatChip extends StatelessWidget {
  const _StatChip(this.emoji, this.value, this.label);
  final String emoji;
  final String value;
  final String label;

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.15),
          borderRadius: BorderRadius.circular(10),
        ),
        child: Column(
          children: [
            Text('$emoji $value', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
            Text(label, style: const TextStyle(color: Colors.white70, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}

class _MotivationCardWidget extends StatelessWidget {
  const _MotivationCardWidget({required this.card});
  final MotivationCard card;

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(card.emoji, style: const TextStyle(fontSize: 28)),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(card.title, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)),
                const SizedBox(height: 4),
                Text(card.text, style: const TextStyle(color: AppColors.mutedForeground, height: 1.4, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';

class FatTrackerScreen extends StatefulWidget {
  const FatTrackerScreen({super.key});

  @override
  State<FatTrackerScreen> createState() => _FatTrackerScreenState();
}

class _FatTrackerScreenState extends State<FatTrackerScreen> {
  final _waist = TextEditingController();
  final _hip = TextEditingController();
  final _neck = TextEditingController();
  final _goal = TextEditingController();
  bool _loading = false;
  String? _result;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (_goal.text.isEmpty) {
      final g = context.read<AppState>().profile?.goalFatPercent;
      if (g != null) _goal.text = g.toStringAsFixed(1);
    }
  }

  Future<void> _submit() async {
    final waist = double.tryParse(_waist.text.replaceAll(',', '.'));
    final hip = double.tryParse(_hip.text.replaceAll(',', '.'));
    if (waist == null || hip == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Введите талию и бёдра')));
      return;
    }
    setState(() {
      _loading = true;
      _result = null;
    });
    try {
      final neck = double.tryParse(_neck.text.replaceAll(',', '.'));
      final goal = double.tryParse(_goal.text.replaceAll(',', '.'));
      final m = await context.read<AppState>().measureFat(
            waist: waist,
            hip: hip,
            neck: neck,
            goal: goal,
          );
      setState(() {
        _result = '${m.emoji} ${m.fatPercent.toStringAsFixed(1)}% — ${m.category}\n(${m.method})';
      });
    } catch (e) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('$e')));
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final history = context.watch<AppState>().fatHistory;
    final isMale = context.watch<AppState>().profile?.gender == 'male';

    return Scaffold(
      appBar: AppBar(title: const Text('Трекер жировой массы')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          AppCard(
            gradient: true,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SectionTitle('Новый замер', icon: Icons.straighten),
                const SizedBox(height: 8),
                const Text(
                  'Измерь обхват талии в самой узкой части и бёдер. Для мужчин — ещё шею (под кадыком).',
                  style: TextStyle(color: AppColors.mutedForeground, fontSize: 13, height: 1.4),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _waist,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Талия (см)', prefixIcon: Icon(Icons.height)),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _hip,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Бёдра (см)', prefixIcon: Icon(Icons.accessibility_new)),
                ),
                if (isMale) ...[
                  const SizedBox(height: 12),
                  TextField(
                    controller: _neck,
                    keyboardType: const TextInputType.numberWithOptions(decimal: true),
                    decoration: const InputDecoration(labelText: 'Шея (см)', prefixIcon: Icon(Icons.person)),
                  ),
                ],
                const SizedBox(height: 12),
                TextField(
                  controller: _goal,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: const InputDecoration(labelText: 'Цель % жира (опционально)', prefixIcon: Icon(Icons.flag)),
                ),
                if (_result != null) ...[
                  const SizedBox(height: 16),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(14),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(_result!, style: const TextStyle(fontWeight: FontWeight.w600)),
                  ),
                ],
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: _loading ? null : _submit,
                  child: Text(_loading ? 'Считаем...' : 'Рассчитать и сохранить'),
                ),
              ],
            ),
          ),
          if (history.isNotEmpty) ...[
            const SizedBox(height: 16),
            const SectionTitle('История', icon: Icons.history),
            const SizedBox(height: 8),
            ...history.map((h) => AppCard(
                  child: ListTile(
                    contentPadding: EdgeInsets.zero,
                    title: Text('${(h['body_fat_percent'] as num).toStringAsFixed(1)}%'),
                    subtitle: Text('${h['date']} · талия ${h['waist_cm']} см'),
                    trailing: h['goal_fat_percent'] != null
                        ? Text('цель ${(h['goal_fat_percent'] as num).toStringAsFixed(1)}%')
                        : null,
                  ),
                )),
          ],
        ],
      ),
    );
  }
}

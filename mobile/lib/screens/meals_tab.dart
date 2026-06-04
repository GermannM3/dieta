import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';

class MealsTab extends StatelessWidget {
  const MealsTab({super.key});

  static Future<void> showAddMeal(BuildContext context) async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const AddMealScreen()),
    );
  }

  String _mealType(String? time) {
    if (time == null) return 'Перекус';
    final hour = int.tryParse(time.split(':').first) ?? 12;
    if (hour < 11) return 'Завтрак';
    if (hour < 15) return 'Обед';
    if (hour < 18) return 'Полдник';
    return 'Ужин';
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final meals = state.todayMeals;

    if (meals.isEmpty) {
      return Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('🍽️', style: TextStyle(fontSize: 48)),
            const SizedBox(height: 12),
            const Text('Нет записей за сегодня'),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: () => showAddMeal(context),
              child: const Text('Добавить приём пищи'),
            ),
          ],
        ),
      );
    }

    return RefreshIndicator(
      onRefresh: state.refreshData,
      child: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: meals.length,
        separatorBuilder: (_, __) => const SizedBox(height: 8),
        itemBuilder: (context, i) {
          final meal = meals[i];
          return Dismissible(
            key: ValueKey(meal.id),
            direction: DismissDirection.endToStart,
            background: Container(
              alignment: Alignment.centerRight,
              padding: const EdgeInsets.only(right: 20),
              color: AppColors.healthDanger,
              child: const Icon(Icons.delete, color: Colors.white),
            ),
            confirmDismiss: (_) async {
              if (meal.id == null) return false;
              await state.deleteMeal(meal.id!);
              return true;
            },
            child: AppCard(
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      _mealType(meal.time),
                      style: const TextStyle(color: AppColors.primary, fontSize: 12),
                    ),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(meal.foodName, style: const TextStyle(fontWeight: FontWeight.w600)),
                        Text(
                          '${meal.weightGrams.toStringAsFixed(0)} г · Б${meal.protein.toStringAsFixed(0)} Ж${meal.fat.toStringAsFixed(0)} У${meal.carbs.toStringAsFixed(0)}',
                          style: const TextStyle(color: AppColors.mutedForeground, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                  Text(
                    '${meal.calories.toStringAsFixed(0)} ккал',
                    style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.primary),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class AddMealScreen extends StatefulWidget {
  const AddMealScreen({super.key});

  @override
  State<AddMealScreen> createState() => _AddMealScreenState();
}

class _AddMealScreenState extends State<AddMealScreen> {
  final _foodController = TextEditingController();
  final _weightController = TextEditingController(text: '100');
  List<Map<String, dynamic>> suggestions = [];
  NutritionResult? nutrition;
  bool searching = false;
  bool calculating = false;
  bool saving = false;

  Future<void> _search(String q) async {
    if (q.length < 2) return;
    setState(() => searching = true);
    try {
      final api = context.read<AppState>().api;
      final results = await api.searchFood(q);
      setState(() => suggestions = results.take(8).toList());
    } catch (_) {
      setState(() => suggestions = []);
    } finally {
      setState(() => searching = false);
    }
  }

  Future<void> _calculate() async {
    final name = _foodController.text.trim();
    final weight = double.tryParse(_weightController.text) ?? 100;
    if (name.isEmpty) return;
    setState(() {
      calculating = true;
      nutrition = null;
    });
    try {
      final api = context.read<AppState>().api;
      final result = await api.calculateCalories(name, weight);
      setState(() => nutrition = result);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      setState(() => calculating = false);
    }
  }

  Future<void> _save() async {
    if (nutrition == null) {
      await _calculate();
      if (nutrition == null) return;
    }
    setState(() => saving = true);
    try {
      final now = DateTime.now();
      final meal = MealModel(
        foodName: _foodController.text.trim(),
        weightGrams: double.parse(_weightController.text),
        calories: nutrition!.calories,
        protein: nutrition!.protein,
        fat: nutrition!.fat,
        carbs: nutrition!.carbs,
        date: now.toIso8601String().split('T').first,
        time: '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:00',
      );
      await context.read<AppState>().addMeal(meal);
      if (mounted) Navigator.pop(context);
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Добавить еду')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          TextField(
            controller: _foodController,
            decoration: InputDecoration(
              labelText: 'Продукт или блюдо',
              suffixIcon: searching
                  ? const Padding(
                      padding: EdgeInsets.all(12),
                      child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)),
                    )
                  : IconButton(icon: const Icon(Icons.search), onPressed: () => _search(_foodController.text)),
            ),
            onChanged: _search,
          ),
          if (suggestions.isNotEmpty)
            ...suggestions.map((s) => ListTile(
                  title: Text(s['name']?.toString() ?? ''),
                  subtitle: Text('${s['calories_per_100g']} ккал/100г'),
                  onTap: () {
                    _foodController.text = s['name']?.toString() ?? '';
                    setState(() => suggestions = []);
                    _calculate();
                  },
                )),
          const SizedBox(height: 12),
          TextField(
            controller: _weightController,
            keyboardType: TextInputType.number,
            decoration: const InputDecoration(labelText: 'Вес (граммы)'),
          ),
          const SizedBox(height: 16),
          OutlinedButton(
            onPressed: calculating ? null : _calculate,
            child: calculating ? const Text('Считаем...') : const Text('Рассчитать калории (ИИ)'),
          ),
          if (nutrition != null) ...[
            const SizedBox(height: 16),
            AppCard(
              gradient: true,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('${nutrition!.calories.toStringAsFixed(0)} ккал',
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.primary)),
                  Text(
                    'Б ${nutrition!.protein.toStringAsFixed(1)} · Ж ${nutrition!.fat.toStringAsFixed(1)} · У ${nutrition!.carbs.toStringAsFixed(1)}',
                    style: const TextStyle(color: AppColors.mutedForeground),
                  ),
                ],
              ),
            ),
          ],
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: saving ? null : _save,
            child: saving ? const Text('Сохранение...') : const Text('Добавить в дневник'),
          ),
        ],
      ),
    );
  }
}

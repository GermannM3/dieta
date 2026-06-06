import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';
import '../widgets/telegram_link.dart';
import '../widgets/update_checker.dart';
import 'home_shell.dart';

class ProfileTab extends StatefulWidget {
  const ProfileTab({super.key, this.forceSetup = false});

  final bool forceSetup;

  @override
  State<ProfileTab> createState() => _ProfileTabState();
}

class _ProfileTabState extends State<ProfileTab> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _name;
  late TextEditingController _age;
  late TextEditingController _weight;
  late TextEditingController _height;
  String? _gender;
  double _activity = 1.375;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final p = context.read<AppState>().profile;
    _name = TextEditingController(text: p?.name ?? '');
    _age = TextEditingController(text: p?.age?.toString() ?? '');
    _weight = TextEditingController(text: p?.weight?.toString() ?? '');
    _height = TextEditingController(text: p?.height?.toString() ?? '');
    _gender = p?.gender ?? 'male';
    _activity = p?.activityLevel ?? 1.375;
  }

  double _calcTarget() {
    final age = int.tryParse(_age.text) ?? 30;
    final weight = double.tryParse(_weight.text) ?? 70;
    final height = double.tryParse(_height.text) ?? 170;
    double bmr;
    if (_gender == 'male' || _gender == 'м') {
      bmr = 10 * weight + 6.25 * height - 5 * age + 5;
    } else {
      bmr = 10 * weight + 6.25 * height - 5 * age - 161;
    }
    return bmr * _activity;
  }

  Future<void> _save() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);
    try {
      final profile = ProfileModel(
        name: _name.text.trim(),
        gender: _gender,
        age: int.parse(_age.text),
        weight: double.parse(_weight.text),
        height: double.parse(_height.text),
        activityLevel: _activity,
        dailyTarget: _calcTarget(),
      );
      await context.read<AppState>().saveProfile(profile);
      if (mounted && widget.forceSetup) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const HomeShell()),
        );
      } else if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Профиль сохранён')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(e.toString())));
      }
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final target = _calcTarget();

    return Scaffold(
      appBar: widget.forceSetup
          ? AppBar(title: const Text('Настройка профиля'), automaticallyImplyLeading: false)
          : null,
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (widget.forceSetup)
            const Padding(
              padding: EdgeInsets.only(bottom: 16),
              child: Text(
                'Заполните профиль для расчёта дневной нормы калорий',
                style: TextStyle(color: AppColors.mutedForeground),
              ),
            ),
          AppCard(
            gradient: true,
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SectionTitle('Ваш профиль', icon: Icons.person),
                  const SizedBox(height: 16),
                  TextFormField(
                    controller: _name,
                    decoration: const InputDecoration(labelText: 'Имя'),
                    validator: (v) => v == null || v.isEmpty ? 'Обязательно' : null,
                  ),
                  const SizedBox(height: 12),
                  DropdownButtonFormField<String>(
                    value: _gender,
                    decoration: const InputDecoration(labelText: 'Пол'),
                    items: const [
                      DropdownMenuItem(value: 'male', child: Text('Мужской')),
                      DropdownMenuItem(value: 'female', child: Text('Женский')),
                    ],
                    onChanged: (v) => setState(() => _gender = v),
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Expanded(
                        child: TextFormField(
                          controller: _age,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: 'Возраст'),
                          validator: (v) => int.tryParse(v ?? '') == null ? 'Число' : null,
                        ),
                      ),
                      const SizedBox(width: 12),
                      Expanded(
                        child: TextFormField(
                          controller: _weight,
                          keyboardType: TextInputType.number,
                          decoration: const InputDecoration(labelText: 'Вес (кг)'),
                          validator: (v) => double.tryParse(v ?? '') == null ? 'Число' : null,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _height,
                    keyboardType: TextInputType.number,
                    decoration: const InputDecoration(labelText: 'Рост (см)'),
                    validator: (v) => double.tryParse(v ?? '') == null ? 'Число' : null,
                  ),
                  const SizedBox(height: 12),
                  const Text('Активность', style: TextStyle(fontWeight: FontWeight.w500)),
                  Slider(
                    value: _activity,
                    min: 1.2,
                    max: 1.9,
                    divisions: 7,
                    label: _activity.toStringAsFixed(2),
                    onChanged: (v) => setState(() => _activity = v),
                  ),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.primary.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      'Дневная норма: ${target.toStringAsFixed(0)} ккал',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: AppColors.primary,
                        fontSize: 16,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: _saving ? null : _save,
                    child: Text(_saving ? 'Сохранение...' : 'Сохранить профиль'),
                  ),
                ],
              ),
            ),
          ),
          if (!widget.forceSetup) ...[
            const SizedBox(height: 16),
            const AppUpdateSection(),
            const SizedBox(height: 16),
            AppCard(
              child: Column(
                children: const [
                  TelegramBotTile(),
                ],
              ),
            ),
            const SizedBox(height: 16),
            AppCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const SectionTitle('Аккаунт', icon: Icons.email),
                  const SizedBox(height: 8),
                  Text(state.user?.email ?? '', style: const TextStyle(color: AppColors.mutedForeground)),
                  if (state.profile?.isPremium == true)
                    const Padding(
                      padding: EdgeInsets.only(top: 8),
                      child: Chip(
                        label: Text('Premium'),
                        backgroundColor: AppColors.healthWarning,
                      ),
                    ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}

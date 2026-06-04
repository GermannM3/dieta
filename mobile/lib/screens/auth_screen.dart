import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import 'home_shell.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _boot();
  }

  Future<void> _boot() async {
    final state = context.read<AppState>();
    await state.init();
    if (!mounted) return;
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => state.token != null ? const HomeShell() : const WelcomeScreen(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: AppTheme.heroGradient,
        child: const Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('🥗', style: TextStyle(fontSize: 64)),
              SizedBox(height: 16),
              Text(
                'Твой Диетолог',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 24),
              CircularProgressIndicator(),
            ],
          ),
        ),
      ),
    );
  }
}

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: AppTheme.heroGradient,
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              children: [
                Align(
                  alignment: Alignment.topRight,
                  child: TextButton.icon(
                    onPressed: () {},
                    icon: const Icon(Icons.telegram, color: AppColors.accent),
                    label: const Text('@tvoy_diet_bot', style: TextStyle(color: AppColors.accent)),
                  ),
                ),
                const Spacer(),
                const Text('🥗', style: TextStyle(fontSize: 72)),
                const SizedBox(height: 16),
                const Text(
                  'Трекер Калорий',
                  style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 8),
                const Text(
                  'Персональный ИИ-диетолог в кармане.\nСчитай калории, следи за водой и достигай целей.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppColors.mutedForeground, height: 1.5),
                ),
                const Spacer(),
                ElevatedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const AuthScreen(isRegister: false)),
                  ),
                  child: const Text('Войти / Регистрация'),
                ),
                const SizedBox(height: 12),
                OutlinedButton(
                  onPressed: () => Navigator.push(
                    context,
                    MaterialPageRoute(builder: (_) => const AuthScreen(isRegister: true)),
                  ),
                  child: const Text('Создать аккаунт'),
                ),
                const SizedBox(height: 32),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class AuthScreen extends StatefulWidget {
  const AuthScreen({super.key, required this.isRegister});

  final bool isRegister;

  @override
  State<AuthScreen> createState() => _AuthScreenState();
}

class _AuthScreenState extends State<AuthScreen> {
  final _formKey = GlobalKey<FormState>();
  final _email = TextEditingController();
  final _password = TextEditingController();
  final _name = TextEditingController();
  late bool register;
  bool loading = false;
  String? error;

  @override
  void initState() {
    super.initState();
    register = widget.isRegister;
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() {
      loading = true;
      error = null;
    });
    try {
      final state = context.read<AppState>();
      if (register) {
        await state.register(_email.text.trim(), _password.text, _name.text.trim());
      } else {
        await state.login(_email.text.trim(), _password.text);
      }
      if (!mounted) return;
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const HomeShell()),
        (_) => false,
      );
    } catch (e) {
      setState(() => error = e.toString());
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(register ? 'Регистрация' : 'Вход')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              if (register)
                TextFormField(
                  controller: _name,
                  decoration: const InputDecoration(labelText: 'Имя'),
                  validator: (v) => v == null || v.isEmpty ? 'Введите имя' : null,
                ),
              if (register) const SizedBox(height: 12),
              TextFormField(
                controller: _email,
                keyboardType: TextInputType.emailAddress,
                decoration: const InputDecoration(labelText: 'Email'),
                validator: (v) =>
                    v == null || !v.contains('@') ? 'Введите корректный email' : null,
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _password,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'Пароль'),
                validator: (v) => v == null || v.length < 6 ? 'Минимум 6 символов' : null,
              ),
              if (error != null) ...[
                const SizedBox(height: 12),
                Text(error!, style: const TextStyle(color: AppColors.healthDanger)),
              ],
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: loading ? null : _submit,
                child: loading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text(register ? 'Зарегистрироваться' : 'Войти'),
              ),
              TextButton(
                onPressed: () => setState(() => register = !register),
                child: Text(register ? 'Уже есть аккаунт? Войти' : 'Нет аккаунта? Регистрация'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

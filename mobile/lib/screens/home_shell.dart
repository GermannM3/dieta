import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import '../theme/app_theme.dart';
import 'auth_screen.dart';
import 'dashboard_tab.dart';
import 'meals_tab.dart';
import 'progress_tab.dart';
import 'dietolog_tab.dart';
import 'profile_tab.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  static const _titles = ['Главная', 'Питание', 'Прогресс', 'Диетолог', 'Профиль'];

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    if (state.profile != null && !state.profile!.isComplete) {
      return const ProfileTab(forceSetup: true);
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(_titles[_index]),
        actions: [
          if ((state.profile?.consciousStreak ?? 0) > 0)
            Padding(
              padding: const EdgeInsets.only(right: 4),
              child: Center(
                child: Chip(
                  label: Text('🔥 ${state.profile!.consciousStreak}'),
                  backgroundColor: AppColors.primary.withOpacity(0.12),
                  side: BorderSide.none,
                  padding: EdgeInsets.zero,
                ),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await state.logout();
              if (!context.mounted) return;
              Navigator.of(context).pushAndRemoveUntil(
                MaterialPageRoute(builder: (_) => const WelcomeScreen()),
                (_) => false,
              );
            },
          ),
        ],
      ),
      body: IndexedStack(
        index: _index,
        children: const [
          DashboardTab(),
          MealsTab(),
          ProgressTab(),
          DietologTab(),
          ProfileTab(),
        ],
      ),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (i) => setState(() => _index = i),
        labelBehavior: NavigationDestinationLabelBehavior.alwaysShow,
        destinations: const [
          NavigationDestination(icon: Icon(Icons.home_outlined), selectedIcon: Icon(Icons.home), label: 'Главная'),
          NavigationDestination(icon: Icon(Icons.restaurant_outlined), selectedIcon: Icon(Icons.restaurant), label: 'Еда'),
          NavigationDestination(icon: Icon(Icons.trending_up_outlined), selectedIcon: Icon(Icons.trending_up), label: 'Прогресс'),
          NavigationDestination(icon: Icon(Icons.psychology_outlined), selectedIcon: Icon(Icons.psychology), label: 'Диетолог'),
          NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Профиль'),
        ],
      ),
      floatingActionButton: _index == 1
          ? FloatingActionButton(
              backgroundColor: AppColors.primary,
              onPressed: () => MealsTab.showAddMeal(context),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
    );
  }
}

import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_state.dart';
import 'auth_screen.dart';
import 'dashboard_tab.dart';
import 'meals_tab.dart';
import 'dietolog_tab.dart';
import 'profile_tab.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  final _tabs = const [
    DashboardTab(),
    MealsTab(),
    DietologTab(),
    ProfileTab(),
  ];

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    if (state.profile != null && !state.profile!.isComplete) {
      return const ProfileTab(forceSetup: true);
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(['Главная', 'Питание', 'Диетолог', 'Профиль'][_index]),
        actions: [
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
      body: _tabs[_index],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _index,
        onTap: (i) => setState(() => _index = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: 'Главная'),
          BottomNavigationBarItem(icon: Icon(Icons.restaurant_outlined), activeIcon: Icon(Icons.restaurant), label: 'Питание'),
          BottomNavigationBarItem(icon: Icon(Icons.psychology_outlined), activeIcon: Icon(Icons.psychology), label: 'Диетолог'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline), activeIcon: Icon(Icons.person), label: 'Профиль'),
        ],
      ),
      floatingActionButton: _index == 1
          ? FloatingActionButton(
              backgroundColor: Theme.of(context).colorScheme.primary,
              onPressed: () => MealsTab.showAddMeal(context),
              child: const Icon(Icons.add, color: Colors.white),
            )
          : null,
    );
  }
}

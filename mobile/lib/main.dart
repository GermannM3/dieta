import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/app_config.dart';
import 'providers/app_state.dart';
import 'screens/auth_screen.dart';
import 'services/api_service.dart';
import 'theme/app_theme.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const TvoyDietologApp());
}

class TvoyDietologApp extends StatelessWidget {
  const TvoyDietologApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider(
      create: (_) => AppState(ApiService()),
      child: MaterialApp(
        title: AppConfig.appName,
        theme: AppTheme.light,
        debugShowCheckedModeBanner: false,
        home: const SplashScreen(),
      ),
    );
  }
}

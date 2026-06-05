/// Конфигурация приложения. Значения подставляются при сборке через
/// --dart-define-from-file=dart_defines.json (GitHub Actions + Secrets).
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://5.129.198.80:8000',
  );

  static const appName = String.fromEnvironment(
    'APP_NAME',
    defaultValue: 'Твой Диетолог',
  );

  static const githubRepo = String.fromEnvironment(
    'GITHUB_REPO',
    defaultValue: 'GermannM3/dieta',
  );

  static String get apiUrl => apiBaseUrl.endsWith('/')
      ? '${apiBaseUrl}api'
      : '$apiBaseUrl/api';
}

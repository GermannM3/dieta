import 'package:flutter/material.dart';
import 'package:ota_update/ota_update.dart';
import 'package:package_info_plus/package_info_plus.dart';

import '../theme/app_theme.dart';
import '../widgets/common_widgets.dart';
import '../services/update_service.dart';

/// Проверяет обновления на GitHub и предлагает скачать APK.
class UpdateChecker {
  UpdateChecker({UpdateService? service}) : _service = service ?? UpdateService();

  final UpdateService _service;

  Future<void> checkAndPrompt(
    BuildContext context, {
    bool silent = false,
  }) async {
    try {
      final update = await _service.checkForUpdate();
      if (update == null || !context.mounted) return;
      await _showUpdateDialog(context, update);
    } catch (e) {
      if (!silent && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Не удалось проверить обновления: $e')),
        );
      }
    }
  }

  Future<void> _showUpdateDialog(BuildContext context, AppUpdateInfo update) async {
    await showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        title: const Text('Доступно обновление'),
        content: Text(
          'Версия ${update.version} уже на GitHub.\n\n'
          'Скачать и установить поверх текущей версии?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Позже'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.pop(ctx);
              _installUpdate(context, update);
            },
            child: const Text('Обновить'),
          ),
        ],
      ),
    );
  }

  Future<void> _installUpdate(BuildContext context, AppUpdateInfo update) async {
    if (!context.mounted) return;

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (ctx) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Скачиваем обновление...'),
          ],
        ),
      ),
    );

    try {
      await for (final event in OtaUpdate().execute(
        update.apkUrl,
        destinationFilename: 'tvoy_dietolog_update.apk',
      )) {
        if (!context.mounted) return;
        if (event.status == OtaStatus.INSTALLING) {
          Navigator.of(context, rootNavigator: true).pop();
        } else if (event.status == OtaStatus.PERMISSION_NOT_GRANTED_ERROR) {
          Navigator.of(context, rootNavigator: true).pop();
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Разрешите установку из неизвестных источников для приложения'),
            ),
          );
          return;
        } else if (event.status == OtaStatus.INTERNAL_ERROR ||
            event.status == OtaStatus.DOWNLOAD_ERROR) {
          Navigator.of(context, rootNavigator: true).pop();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Ошибка обновления: ${event.value ?? event.status}')),
          );
          return;
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Ошибка: $e')),
        );
      }
    }
  }
}

class AppUpdateSection extends StatefulWidget {
  const AppUpdateSection({super.key});

  @override
  State<AppUpdateSection> createState() => _AppUpdateSectionState();
}

class _AppUpdateSectionState extends State<AppUpdateSection> {
  String _version = '...';
  bool _checking = false;
  final _checker = UpdateChecker();

  @override
  void initState() {
    super.initState();
    _loadVersion();
  }

  Future<void> _loadVersion() async {
    final info = await PackageInfo.fromPlatform();
    if (mounted) {
      setState(() => _version = '${info.version} (${info.buildNumber})');
    }
  }

  Future<void> _check() async {
    setState(() => _checking = true);
    try {
      await _checker.checkAndPrompt(context);
    } finally {
      if (mounted) setState(() => _checking = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SectionTitle('Обновление приложения', icon: Icons.system_update),
          const SizedBox(height: 8),
          Text('Текущая версия: $_version', style: const TextStyle(color: AppColors.mutedForeground)),
          const SizedBox(height: 12),
          OutlinedButton.icon(
            onPressed: _checking ? null : _check,
            icon: _checking
                ? const SizedBox(
                    width: 16,
                    height: 16,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.refresh),
            label: Text(_checking ? 'Проверяем...' : 'Проверить обновления'),
          ),
        ],
      ),
    );
  }
}

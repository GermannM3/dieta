import 'package:flutter/material.dart';
import 'package:flutter_rustore_update/flutter_rustore_update.dart';
import 'package:ota_update/ota_update.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:url_launcher/url_launcher.dart';

import '../config/app_config.dart';
import '../services/update_service.dart';
import '../theme/app_theme.dart';
import 'common_widgets.dart';

/// Сначала RuStore (если приложение установлено из стора), иначе GitHub Releases.
class UpdateChecker {
  UpdateChecker({UpdateService? github}) : _github = github ?? UpdateService();

  final UpdateService _github;

  Future<void> checkAndPrompt(
    BuildContext context, {
    bool silent = false,
  }) async {
    try {
      if (await _checkRustore(context, silent: silent)) return;
      await _checkGithub(context, silent: silent);
    } catch (e) {
      if (!silent && context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Не удалось проверить обновления: $e')),
        );
      }
    }
  }

  Future<bool> _checkRustore(BuildContext context, {required bool silent}) async {
    try {
      final info = await RustoreUpdateClient.info();
      if (info.updateAvailabilityValue != UpdateAvailability.available || !context.mounted) {
        return false;
      }

      await showDialog<void>(
        context: context,
        builder: (ctx) => AlertDialog(
          title: const Text('Доступно обновление'),
          content: const Text(
            'Новая версия уже в RuStore.\n\nСкачать и установить?',
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Позже')),
            FilledButton(
              onPressed: () {
                Navigator.pop(ctx);
                _runRustoreUpdate(context);
              },
              child: const Text('Обновить'),
            ),
          ],
        ),
      );
      return true;
    } catch (_) {
      return false;
    }
  }

  Future<void> _runRustoreUpdate(BuildContext context) async {
    if (!context.mounted) return;

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            CircularProgressIndicator(),
            SizedBox(height: 16),
            Text('Загружаем обновление из RuStore...'),
          ],
        ),
      ),
    );

    RustoreUpdateClient.listener((state) async {
      if (!context.mounted) return;
      if (state.installStatus == INSTALL_STATUS_DOWNLOADED) {
        Navigator.of(context, rootNavigator: true).pop();
        await RustoreUpdateClient.completeUpdateFlexible();
      } else if (state.installStatus == INSTALL_STATUS_FAILED) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Ошибка обновления через RuStore')),
        );
      }
    });

    try {
      await RustoreUpdateClient.download();
    } catch (e) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('RuStore: $e')),
        );
      }
    }
  }

  Future<void> _checkGithub(BuildContext context, {required bool silent}) async {
    final update = await _github.checkForUpdate();
    if (update == null || !context.mounted) return;

    await showDialog<void>(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => AlertDialog(
        title: const Text('Доступно обновление'),
        content: Text(
          'Версия ${update.version}.\n\n'
          'Скачать APK с GitHub и установить?',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Позже')),
          FilledButton(
            onPressed: () {
              Navigator.pop(ctx);
              _installGithubApk(context, update);
            },
            child: const Text('Обновить'),
          ),
        ],
      ),
    );
  }

  Future<void> _installGithubApk(BuildContext context, AppUpdateInfo update) async {
    if (!context.mounted) return;

    showDialog<void>(
      context: context,
      barrierDismissible: false,
      builder: (_) => const AlertDialog(
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
              content: Text('Разрешите установку из неизвестных источников'),
            ),
          );
          return;
        } else if (event.status == OtaStatus.INTERNAL_ERROR ||
            event.status == OtaStatus.DOWNLOAD_ERROR) {
          Navigator.of(context, rootNavigator: true).pop();
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Ошибка: ${event.value ?? event.status}')),
          );
          return;
        }
      }
    } catch (e) {
      if (context.mounted) {
        Navigator.of(context, rootNavigator: true).pop();
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Ошибка: $e')));
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
    if (mounted) setState(() => _version = '${info.version} (${info.buildNumber})');
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
                ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2))
                : const Icon(Icons.refresh),
            label: Text(_checking ? 'Проверяем...' : 'Проверить обновления'),
          ),
        ],
      ),
    );
  }
}

class RustoreLinkTile extends StatelessWidget {
  const RustoreLinkTile({super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: AppColors.primary.withOpacity(0.12),
        child: const Icon(Icons.shop, color: AppColors.primary),
      ),
      title: const Text('RuStore'),
      subtitle: const Text('Скачать или обновить через магазин'),
      trailing: const Icon(Icons.open_in_new, size: 20),
      onTap: () async {
        final uri = Uri.parse(AppConfig.rustoreAppUrl);
        if (!await launchUrl(uri, mode: LaunchMode.externalApplication) && context.mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Не удалось открыть RuStore')),
          );
        }
      },
    );
  }
}

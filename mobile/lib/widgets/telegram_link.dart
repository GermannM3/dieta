import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../config/app_config.dart';
import '../theme/app_theme.dart';

/// Opens Telegram bot in the Telegram app or browser.
Future<void> openTelegramBot() async {
  final uri = Uri.parse(AppConfig.telegramBotUrl);
  if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
    throw Exception('Не удалось открыть Telegram');
  }
}

class TelegramBotButton extends StatelessWidget {
  const TelegramBotButton({
    super.key,
    this.compact = false,
    this.outlined = false,
  });

  final bool compact;
  final bool outlined;

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return TextButton.icon(
        onPressed: () => _open(context),
        icon: const Icon(Icons.telegram, color: AppColors.accent),
        label: Text(
          AppConfig.telegramBotUsername,
          style: const TextStyle(color: AppColors.accent),
        ),
      );
    }

    if (outlined) {
      return OutlinedButton.icon(
        onPressed: () => _open(context),
        icon: const Icon(Icons.telegram),
        label: const Text('Открыть бота в Telegram'),
      );
    }

    return ElevatedButton.icon(
      onPressed: () => _open(context),
      style: ElevatedButton.styleFrom(
        backgroundColor: const Color(0xFF229ED9),
        foregroundColor: Colors.white,
      ),
      icon: const Icon(Icons.telegram),
      label: const Text('Telegram-бот'),
    );
  }

  Future<void> _open(BuildContext context) async {
    try {
      await openTelegramBot();
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    }
  }
}

class TelegramBotTile extends StatelessWidget {
  const TelegramBotTile({super.key});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        backgroundColor: const Color(0xFF229ED9).withOpacity(0.15),
        child: const Icon(Icons.telegram, color: Color(0xFF229ED9)),
      ),
      title: const Text('Telegram-бот'),
      subtitle: Text(AppConfig.telegramBotUsername),
      trailing: const Icon(Icons.open_in_new, size: 20),
      onTap: () async {
        try {
          await openTelegramBot();
        } catch (e) {
          if (context.mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(content: Text(e.toString())),
            );
          }
        }
      },
    );
  }
}

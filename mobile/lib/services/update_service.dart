import 'dart:convert';

import 'package:http/http.dart' as http;
import 'package:package_info_plus/package_info_plus.dart';

import '../config/app_config.dart';

/// Информация о доступном обновлении с GitHub Releases.
class AppUpdateInfo {
  const AppUpdateInfo({
    required this.version,
    required this.buildNumber,
    required this.apkUrl,
    required this.tag,
    this.releaseNotes,
  });

  final String version;
  final int buildNumber;
  final String apkUrl;
  final String tag;
  final String? releaseNotes;
}

class UpdateService {
  UpdateService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  static const githubRepo = AppConfig.githubRepo;

  /// Сравнивает semver: true если [remote] новее [current].
  static bool isVersionNewer(String remote, String current) {
    final r = remote.split('.').map(int.parse).toList();
    final c = current.split('.').map(int.parse).toList();
    while (r.length < 3) {
      r.add(0);
    }
    while (c.length < 3) {
      c.add(0);
    }
    for (var i = 0; i < 3; i++) {
      if (r[i] > c[i]) return true;
      if (r[i] < c[i]) return false;
    }
    return false;
  }

  static int _buildFromRelease(Map<String, dynamic> release, String version) {
    final body = release['body'] as String? ?? '';
    final match = RegExp(r'buildNumber:\s*(\d+)', caseSensitive: false).firstMatch(body);
    if (match != null) return int.parse(match.group(1)!);
    // Fallback: derive from semver patch + minor*100 + major*10000
    final parts = version.split('.').map(int.parse).toList();
    while (parts.length < 3) {
      parts.add(0);
    }
    return parts[0] * 10000 + parts[1] * 100 + parts[2];
  }

  Future<AppUpdateInfo?> checkForUpdate() async {
    final pkg = await PackageInfo.fromPlatform();
    final currentVersion = pkg.version;
    final currentBuild = int.tryParse(pkg.buildNumber) ?? 0;

    final res = await _client.get(
      Uri.parse('https://api.github.com/repos/$githubRepo/releases'),
      headers: {'Accept': 'application/vnd.github+json'},
    );
    if (res.statusCode != 200) return null;

    final releases = jsonDecode(res.body) as List<dynamic>;
    AppUpdateInfo? best;

    for (final raw in releases) {
      final release = raw as Map<String, dynamic>;
      final tag = release['tag_name'] as String? ?? '';
      if (!tag.startsWith('android-v')) continue;

      final version = tag.substring('android-v'.length);
      if (!RegExp(r'^\d+\.\d+\.\d+$').hasMatch(version)) continue;

      final buildNumber = _buildFromRelease(release, version);
      final newer = isVersionNewer(version, currentVersion) ||
          (version == currentVersion && buildNumber > currentBuild);
      if (!newer) continue;

      final assets = release['assets'] as List<dynamic>? ?? [];
      String? apkUrl;
      for (final asset in assets) {
        final map = asset as Map<String, dynamic>;
        if (map['name'] == 'app-release.apk') {
          apkUrl = map['browser_download_url'] as String?;
          break;
        }
      }
      if (apkUrl == null) continue;

      final candidate = AppUpdateInfo(
        version: version,
        buildNumber: buildNumber,
        apkUrl: apkUrl,
        tag: tag,
        releaseNotes: release['body'] as String?,
      );

      if (best == null || isVersionNewer(candidate.version, best.version)) {
        best = candidate;
      }
    }

    return best;
  }

  void dispose() => _client.close();
}

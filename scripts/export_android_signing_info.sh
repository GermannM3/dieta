#!/bin/bash
# Выводит SHA-256 отпечаток release-ключа для RuStore / Google Play Console.
set -euo pipefail

KEYSTORE="${1:-mobile/android/app/upload-keystore.jks}"
ALIAS="${2:-upload}"
STORE_PASS="${ANDROID_KEYSTORE_PASSWORD:-DietaUpload2026!}"

if [[ ! -f "$KEYSTORE" ]]; then
  echo "Keystore not found: $KEYSTORE"
  echo "Download from CI cache or generate via android-release workflow."
  exit 1
fi

echo "=== Certificate ($ALIAS) ==="
keytool -list -v -keystore "$KEYSTORE" -alias "$ALIAS" -storepass "$STORE_PASS" 2>/dev/null | \
  grep -E "SHA256:|SHA1:|Owner:|Valid from"

echo ""
echo "Package: com.tvoydietolog.app"
echo "Privacy policy URL: http://5.129.198.80:8000/privacy"

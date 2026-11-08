#!/usr/bin/env bash
# mFk AcilNet ana sayfasını ve sesli telsiz servisini Internet-in-a-Box'a kurar.
# Installs the mFk AcilNet homepage and voice radio service into Internet-in-a-Box.
set -euo pipefail

[ "$EUID" -eq 0 ] || { echo "sudo ile çalıştır / run with sudo" >&2; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/www/home"
DST=/library/www/html/home

[ -d "$DST" ] || { echo "$DST yok. Önce Internet-in-a-Box'ı kur / install Internet-in-a-Box first" >&2; exit 1; }

if [ -f "$DST/index.html" ] && [ ! -f "$DST/index.html.iiab-original" ]; then
  cp "$DST/index.html" "$DST/index.html.iiab-original"
fi
cp "$SRC/"*.html "$DST/"
[ -f "$SRC/favicon.svg" ] && cp "$SRC/favicon.svg" "$DST/"

# Sesli Telsiz Mikro-Servisini Kur (has-voice-service)
if [ -f "$REPO/saglik/has-voice-service.service" ] && command -v systemctl >/dev/null; then
  install -d -m 755 /usr/local/lib/has-voice
  install -m 755 "$REPO/scripts/voice-service.py" /usr/local/lib/has-voice/voice-service.py
  install -m 644 "$REPO/saglik/has-voice-service.service" /etc/systemd/system/has-voice-service.service
  systemctl daemon-reload
  systemctl enable --now has-voice-service.service 2>/dev/null || systemctl restart has-voice-service.service 2>/dev/null || true
  echo "Sesli telsiz servisi devrede / voice service installed (Port 8081)"
fi

echo "Ana sayfa kuruldu / homepage installed: http://box.lan/home"
echo "Geri almak için / to restore: sudo cp $DST/index.html.iiab-original $DST/index.html"

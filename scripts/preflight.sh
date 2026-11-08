#!/usr/bin/env bash
# Kurulum öncesi donanım ve sistem kontrolü (salt okunur) / pre-install hardware and system check (read-only).
# Bobcat / Helium madencisi ve diğer ARM kutular için: kurmadan önce cihazın uygun olup olmadığını söyler.
# Kullanım / usage:  ./scripts/preflight.sh        (install.sh bunu otomatik çalıştırır / install.sh runs it)
# Çıkış kodu / exit code: 0 = uygun ya da yalnız uyarı var / OK or warnings only,  1 = kurulamaz / cannot install
set -uo pipefail

FAIL=0; WARN=0
ok(){   printf '  [ OK ] %s\n' "$*"; }
warn(){ printf '  [UYARI/WARN] %s\n' "$*"; WARN=$((WARN+1)); }
bad(){  printf '  [HATA/FAIL] %s\n' "$*"; FAIL=$((FAIL+1)); }

echo "== Cihaz kontrolü / device check =="

# 1. İşletim sistemi ve mimari
arch=$(uname -m)
if [ -r /etc/os-release ]; then
  . /etc/os-release
  echo "  Sistem / system: ${PRETTY_NAME:-bilinmiyor} ($arch)"
  case "${ID:-}${ID_LIKE:-}" in
    *debian*|*ubuntu*|*raspbian*) ok "Debian tabanlı sistem / Debian-based system" ;;
    *) bad "Debian/Ubuntu/Raspberry Pi OS gerekli. Cihazın kendi (kapalı) yazılımı yerine temiz bir imaj kur / needs a clean Debian-based image, not the vendor firmware." ;;
  esac
else
  bad "/etc/os-release yok / missing: işletim sistemi tanınamadı / cannot identify the OS"
fi
case "$arch" in
  aarch64|arm64|armv7l|x86_64) ok "Mimari desteklenir / architecture supported: $arch" ;;
  *) warn "Mimari test edilmemiş / untested architecture: $arch" ;;
esac
command -v systemctl >/dev/null && ok "systemd var / present" || bad "systemd gerekli / required"
command -v apt-get >/dev/null && ok "apt var / present" || bad "apt gerekli / required"

# 2. Bellek
mem_mb=$(awk '/MemTotal/ {printf "%d", $2/1024}' /proc/meminfo 2>/dev/null || echo 0)
if [ "${mem_mb:-0}" -ge 1800 ]; then ok "RAM: ${mem_mb} MB"
elif [ "${mem_mb:-0}" -ge 900 ]; then warn "RAM az / low: ${mem_mb} MB. Kurulum yavaş olabilir, büyük arşivler zorlanır."
else bad "RAM çok az / too low: ${mem_mb} MB"; fi

# 3. Depolama (/library varsa orası, yoksa /)
target=/library; [ -d "$target" ] || target=/
free_gb=$(df -BG --output=avail "$target" 2>/dev/null | tail -1 | tr -dc '0-9')
echo "  Boş alan / free space ($target): ${free_gb:-?} GB"
if [ -n "${free_gb:-}" ]; then
  if   [ "$free_gb" -ge 100 ]; then ok "Tam liste için yeterli / enough for the full list (config/content.conf)"
  elif [ "$free_gb" -ge 25  ]; then ok "Hafif liste için yeterli / enough for the lite list: sudo ./scripts/download-content.sh config/content-lite.conf"
  elif [ "$free_gb" -ge 8   ]; then warn "Alan az / low: yalnız küçük içerik sığar / only a small subset fits (config/content-lite.conf'u kısalt / trim it)"
  else bad "Alan yetersiz / not enough space: ${free_gb} GB"; fi
fi

# 4. Wi-Fi erişim noktası (AP) desteği: projenin ana fikri
if command -v iw >/dev/null; then
  if [ -z "$(iw dev 2>/dev/null)" ]; then
    warn "Wi-Fi arayüzü bulunamadı / no Wi-Fi interface. Hotspot için AP destekli bir USB Wi-Fi adaptörü gerekir / an AP-capable USB Wi-Fi adapter is needed."
  elif iw list 2>/dev/null | sed -n '/Supported interface modes/,/Band/p' | grep -qE '^\s*\* AP$'; then
    ok "Wi-Fi çipi AP (hotspot) modunu destekliyor / Wi-Fi supports AP mode"
  else
    warn "Wi-Fi çipi AP modunu desteklemiyor görünüyor / Wi-Fi does not report AP mode. Hotspot çalışmaz; AP destekli USB adaptör kullan / use an AP-capable USB adapter."
  fi
else
  warn "'iw' yüklü değil / not installed: AP desteği kontrol edilemedi / cannot check AP support (sudo apt install iw)"
fi

# 5. Pi'ye özel: vcgencmd yoksa düşük voltaj uyarısı çalışmaz (hata değil)
command -v vcgencmd >/dev/null || echo "  Bilgi / note: Raspberry Pi değil; düşük voltaj uyarısı devre dışı / not a Pi, under-voltage warning is disabled."

# 6. İnternet (yalnız kurulum ve içerik indirme sırasında gerekir)
if curl -fsS -m 8 -o /dev/null https://download.kiwix.org/ 2>/dev/null; then ok "İnternet erişimi var / internet reachable"
else warn "İnternet yok / no internet: kurulum ve içerik indirme için gerekli / needed for install and content download"; fi

echo
if [ "$FAIL" -gt 0 ]; then echo "SONUÇ / RESULT: kurulamaz / cannot install ($FAIL hata / failures, $WARN uyarı / warnings)"; exit 1; fi
if [ "$WARN" -gt 0 ]; then echo "SONUÇ / RESULT: kurulabilir, ama $WARN uyarıya bak / installable, but check $WARN warning(s)"; fi
[ "$WARN" -eq 0 ] && echo "SONUÇ / RESULT: uygun / OK"
exit 0

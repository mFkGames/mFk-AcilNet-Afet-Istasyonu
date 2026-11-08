@echo off
chcp 65001 >nul
title mFk AcilNet - Önizleme Sunucusu

echo ============================================================
echo   mFk AcilNet Web Arayüzü Önizleme Başlatıcı
echo ============================================================
echo.

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    echo [OK] Python bulundu, yerel sunucu baslatiliyor...
    echo Tarayici otomatik acilacak: http://localhost:8080/home/
    echo.
    python onizleme_sunucusu.py
) else (
    echo [UYARI] Python bulunamadi, sayfa dogrudan tarayicida aciliyor...
    start "" "%~dp0www\home\index.html"
)

pause

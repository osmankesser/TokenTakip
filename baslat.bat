@echo off
cd /d "%~dp0"
if exist "%~dp0dist\TokenTakip.exe" (
  start "" "%~dp0dist\TokenTakip.exe"
) else if exist "%~dp0TokenTakip.exe" (
  start "" "%~dp0TokenTakip.exe"
) else (
  echo TokenTakip.exe bulunamadi.
  pause
)

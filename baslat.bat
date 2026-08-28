@echo off
cd /d "%~dp0"
if exist "%~dp0TokenTracker.exe" (
  start "" "%~dp0TokenTracker.exe"
) else (
  echo Once _build_deploy.py calistirin.
  pause
)

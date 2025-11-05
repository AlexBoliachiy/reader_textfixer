@echo off
setlocal EnableExtensions

set "OLLAMA_DIR=%LOCALAPPDATA%\Programs\Ollama"

rem Go to the Ollama install folder
cd /d "%OLLAMA_DIR%" || (
  echo Could not find "%OLLAMA_DIR%"
  exit /b 1
)

echo [*] Stopping Ollama Windows service (if running)...
sc stop "Ollama" >nul 2>&1

echo [*] Killing Ollama processes (GUI + CLI)...
for %%I in ("ollama.exe" "Ollama.exe" "ollama app.exe" "Ollama App.exe") do (
  taskkill /F /T /IM "%%~I" >nul 2>&1
)

echo [*] Freeing port 11434 if something else still holds it...
for /f "tokens=5" %%P in ('
  netstat -ano ^| findstr /R /C:":11434 .*LISTENING"
') do (
  taskkill /F /PID %%P >nul 2>&1
)

rem give the OS a moment to release handles
timeout /t 1 /nobreak >nul

echo [*] Starting Ollama server...
.\ollama.exe serve

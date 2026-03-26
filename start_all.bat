@echo off
echo =========================================
echo         Starting Rocket Lab System...
echo =========================================

:: Перевіряємо, чи працює проста команда python, якщо ні — використовуємо повний шлях
set PY_EXE=python
where %PY_EXE% >nul 2>nul
if %errorlevel% neq 0 set PY_EXE=py

:: 1. Запуск веб-сервера (порт 8000, бо ngrok дивиться на нього)
start cmd /k "title Web Server && echo Starting Flask Server... && %PY_EXE% server.py"

:: 2. Запуск бота
start cmd /k "title Telegram Bot && echo Starting Bot... && %PY_EXE% main.py"

:: 3. Запуск тунелю ngrok
start cmd /k "title Ngrok Tunnel && echo Starting Ngrok... && ngrok http --domain=kevin-substructural-luz.ngrok-free.dev 8000"

echo All services launched!
pause
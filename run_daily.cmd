@echo off
rem Lanzador de la tarea programada "XAUUSD senal diaria" (lunes a viernes, 7:00 AM hora del Este).
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist logs mkdir logs
"C:\Users\frami\AppData\Local\Python\pythoncore-3.14-64\python.exe" daily_signal.py >> logs\task.log 2>&1

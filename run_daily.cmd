@echo off
rem Tarea programada "XAUUSD senal diaria" (L-V 7:00 AM ET): solo la senal del agente. La regla mecanica corre en el servidor.
cd /d "%~dp0"
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist logs mkdir logs
"C:\Users\frami\AppData\Local\Python\pythoncore-3.14-64\python.exe" daily_signal.py --agent-only >> logs\task.log 2>&1

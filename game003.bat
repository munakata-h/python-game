@echo off
cd /d %~dp0

:: 1. 仮想環境のPythonを指定して実行
.\venv312\Scripts\python.exe game003.py

pause
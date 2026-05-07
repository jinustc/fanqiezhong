@echo off
cd /d "%~dp0"

"%LocalAppData%\Programs\Python\Python313\python.exe" -c "import sys; sys.path.insert(0, '.'); from PomoClock.main import main; main()"

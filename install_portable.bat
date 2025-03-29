@echo off
cd .
python -m venv venv
call venv/scripts/activate.bat
setlocal enabledelayedexpansion
pip install -r requirements.txt
echo Install completed. Run start_portable.bat
deactivate
pause

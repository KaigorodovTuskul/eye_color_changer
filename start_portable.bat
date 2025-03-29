@echo off
cd .
call venv/scripts/activate.bat
setlocal enabledelayedexpansion

for %%f in (workfolder\*) do (
    echo Processing file: %%f
    python stable_CPU_silent.py --input-source "%%~nxf" --rgb brown --clean-cache
)

echo All files in workfolder directory are completed.
pause

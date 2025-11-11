@echo off
REM Native host launcher script for Windows

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

REM Go to project root
for %%i in ("%SCRIPT_DIR%..\..") do set PROJECT_ROOT=%%~fi

REM Change to project directory
cd /d "%PROJECT_ROOT%"

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

REM Run the native host with Python
python native_host.py 2>> "%SCRIPT_DIR%\native_host_error.log"

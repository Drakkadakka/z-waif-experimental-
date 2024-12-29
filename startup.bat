@echo off
setlocal

REM Get the current directory of the batch file
set "SCRIPT_DIR=%~dp0"

REM Activate the virtual environment if applicable
call "%SCRIPT_DIR%venv\Scripts\activate"

REM Run the main application
python "%SCRIPT_DIR%main.py"

echo.
echo Batch file execution completed. Press any key to exit.
pause >nul

endlocal

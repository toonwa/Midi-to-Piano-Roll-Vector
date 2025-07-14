@echo off
cd /d "%~dp0"
call .\env\Scripts\activate

:menu_loop
cls
echo ========================================
echo Select an option to run a script:
echo.
echo 1 - Check overlap
echo 2 - Midi to Piano Roll
echo 3 - Sustain add
echo 4 - Midi to 20 note organ
echo 0 - Exit to command prompt
echo ========================================
set /p choice="Enter your choice: "
set choice=%choice: =%

if "%choice%"=="1" (
    python checkoverlap.py
) else if "%choice%"=="2" (
    python miditoroll.py
) else if "%choice%"=="3" (
    python sustainadd.py
) else if "%choice%"=="4" (
    python miditoorgan.py
) else if "%choice%"=="0" (
    goto end
) else (
    echo Invalid choice.
)

echo.
pause
goto menu_loop

:end
cmd /k

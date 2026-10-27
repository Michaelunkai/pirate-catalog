@echo off
echo Booty Catalog — Pirate Game Catalog
echo ====================================
echo.

:: Try the C++ EXE first (fastest, all features)
if exist "build\bin\BootyCatalog.exe" (
    echo Launching BootyCatalog.exe...
    start "Booty Catalog" "build\bin\BootyCatalog.exe"
) else if exist "BootyCatalog.exe" (
    echo Launching BootyCatalog.exe...
    start "Booty Catalog" "BootyCatalog.exe"
) else (
    echo BootyCatalog.exe not found, falling back to web...
    echo.
    :: Web mode
    echo [1] Web mode: http://localhost:8080
    echo [2] Desktop mode (requires Python)
    echo.
    choice /c 12 /n /m "Choose (1 or 2):"
    if errorlevel 2 (
        pip install -q flet >nul 2>&1
        python main.py
    ) else (
        python -m http.server 8080
    )
)

echo.
echo Booty Catalog is ready. Every game, every repacker.
pause

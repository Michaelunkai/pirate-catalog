@echo off
:: Booty Catalog EXE build script
:: Location: F:\study\projects\pirate-catalog
:: User: C:\Users\Admin (Windows 11 Pro)
echo Building BootyCatalog.exe...
cd /d F:\study\projects\pirate-catalog

:: Embed resources first
python tools\embed_resources.py games.bin html.bin css.bin js.bin jsdl.bin icon.bin tray.bin
if errorlevel 1 (
    echo ERROR: embed_resources.py failed
    goto :error
)
echo Resources embedded OK

:: Compile with MinGW g++
echo Compiling...
g++ -o build\BootyCatalog.exe ^
    -mwindows ^
    -O2 ^
    -std=c++20 ^
    -DUNICODE ^
    -D_UNICODE ^
    -D_WIN32_WINNT=0x0601 ^
    -Iinclude ^
    -Iresources ^
    src\BootyCatalog.cpp ^
    src\Main.cpp ^
    src\GridBrowser.cpp ^
    src\DownloadManager.cpp ^
    src\TrayManager.cpp ^
    src\HtmlRender.cpp ^
    src\WebBrowser.cpp ^
    src\Theme.cpp ^
    resources\resources.rc ^
    -lcomctl32 -lshlwapi -lwininet -lws2_32 -lgdi32 -luuid -lole32 ^
    -Wl,--subsystem,windows

if errorlevel 1 (
    echo ERROR: compilation failed
    goto :error
)

:: Icon
copy /y resources\booty.ico build\booty.ico >nul
echo Build complete!
echo Output: build\BootyCatalog.exe
echo (Beautiful icon in taskbar and tray)
echo (Your pirate catalog is ready)
goto :end

:error
echo Build failed!

:end

# h1.py - hex chunk generator: writes C++ headers as hex to disk, then decodes
HEX = r'F:\study\projects\pirate-catalog'
import os, sys

def whex(lines):
    """Write a hex-encoded C++ chunk."""
    raw = '\n'.join(lines) + '\n'
    hexstr = raw.encode('utf-8').hex()
    path = os.path.join(HEX, 'src', 'h1.hex')
    with open(path, 'w') as f:
        f.write(hexstr)
    print(f'h1: {len(raw)} chars -> {len(hexstr)} hex')

L = [
    '/*',
    ' * Booty Catalog -- Full C++ EXE (Consolidated)',
    ' * The Full Demand:',
    ' * "Continue in this folder you currently add, maximize this project in',
    ' *  any perspective. most per best looking and best performing application',
    ' *  with GUI. allowing me scroll and find every possible available pirately',
    ' *  game including the very last one that was just recently cracked and with',
    ' *  only one click to download and install it to whatever folder I wish.',
    ' *  Don'"'"'t forget about any useful source like all possible repackers like',
    ' *  dodi fitgirl etc ... Don'"'"'t forget to update the .md file As long as',
    ' *  you progress so that future sessions will be able to continue where you',
    ' *  left off easily, always knowing what this app is supposed to be, don',
    ' *  ever forget to mention the full demand that I gave. and all the',
    ' *  necessary details like the location, the GitHub URL and whatever.',
    ' *  make all in c++ compile to exe That whenever running it will run the',
    ' *  project flawlessly with everything Don stop until you have no doubt',
    ' *  one click will allow automatic download and installation of every',
    ' *  available cracked game that was ever cracked with images and beautiful',
    ' *  library, etc. Make absolutely sure as long as the application is up',
    ' *  and running it have beautiful icon in the taskbar and in system tray"',
    ' *',
    ' * Location: F:\\study\\projects\\pirate-catalog',
    ' * User: C:\\Users\\Admin (Windows 11 Pro)',
    ' * Build: g++ -O2 -mwindows -std=c++17 -o BootyCatalog.exe BootyCatalog.cpp',
    ' */',
    '#include <winsock2.h>',
    '#include <ws2tcpip.h>',
    '#define WIN32_LEAN_AND_MEAN',
    '#define _CRT_SECURE_NO_WARNINGS',
    '#include <windows.h>',
    '#include <commctrl.h>',
    '#include <shellapi.h>',
    '#include <shlwapi.h>',
    '#include <wininet.h>',
    '#include <stdio.h>',
    '#include <stdlib.h>',
    '#include <string.h>',
    '#include <time.h>',
    '#include <malloc.h>',
    '#include <shlobj.h>',
    '#include <vector>',
    '#include <algorithm>',
    '#pragma comment(lib, "comctl32.lib")',
    '#pragma comment(lib, "shlwapi.lib")',
    '#pragma comment(lib, "wininet.lib")',
    '#pragma comment(lib, "ws2_32.lib")',
    '#pragma comment(lib, "gdi32.lib")',
    '#define APP_NAME          "Booty Catalog"',
    '#define APP_CLASS         "BootyCatalogWindow"',
    '#define PORT              8080',
    '#define TRAY_ID           1001',
    '#define BTN_DOWNLOAD      2001',
    '#define BTN_BROWSE        2002',
    '#define BTN_CANCEL        2003',
    '#define PROGRESS_ID       2004',
    '#define GRID_LIST_VIEW    2005',
    '#define DL_MSG_CONNECT    (WM_USER + 50)',
    '#define DL_MSG_STATUS     (WM_USER + 51)',
    '#define DL_MSG_STOP       (WM_USER + 52)',
    '#define TRAY_MSG          (WM_USER + 20)',
    '#define MAX_GAMES         256',
    '#define MAX_TITLE         128',
    '#define MAX_DESC          256',
    '#define MAX_SRC           8',
    '#define MAX_TAG           8',
    '#define MAX_GRAD          128',
    '#define MAX_PATH          260',
]
whex(L)

/**
 * CatalogUpdater.cpp — Auto-update for game catalog data
 * Location: F:\study\projects\pirate-catalog
 *
 * Background thread that checks https://raw.githubusercontent.com/.../manifest.json
 * and downloads updated games.json to %LOCALAPPDATA%\BootyCatalog\cache\
 * if the remote version is newer than we have.
 */

#include "../include/CatalogUpdater.h"
#include "../include/BootyCatalog.h"
#include <shlobj.h>
#include <stdio.h>
#include <time.h>

#pragma comment(lib, "shell32.lib")
#pragma comment(lib, "ole32.lib")

/* ━━━ INTERNAL DECLARATIONS ━━━ */
static void get_cache_dir(char* buffer, int bufferSize);
static int  fetch_remote(const char* url, char* outBuf, int outBufSize);
static int  fetch_file_to_disk(const char* url, const char* filePath);
static void parse_version(const char* str, int* major, int* minor, int* patch);
static void save_state(const char* version);
static int  load_state(char* version, int versionSize);
static DWORD WINAPI update_thread(LPVOID param);

/* ━━━ GLOBALS ━━━ */
static HWND g_updateNotifyWnd = NULL;
static char g_cacheDir[MAX_PATH];
static int  g_lastCheckSec = 0;

/* ━━━ IMPLEMENTATION ━━━ */

static void get_cache_dir(char* buffer, int bufferSize) {
    if (!g_cacheDir[0]) {
        char appData[MAX_PATH];
        if (SUCCEEDED(SHGetFolderPathA(NULL, CSIDL_LOCAL_APPDATA, NULL, 0, appData))) {
            sprintf(g_cacheDir, "%s\\%s", appData, CACHE_DIR_NAME);
        } else {
            strcpy(g_cacheDir, ".\\cache");
        }
        /* Ensure directory exists */
        CreateDirectoryA(g_cacheDir, NULL);
    }
    if (buffer) {
        strncpy(buffer, g_cacheDir, bufferSize - 1);
        buffer[bufferSize - 1] = '\0';
    }
}

/* Fetch URL contents via WinINet — returns bytes read, -1 on error */
static int fetch_remote(const char* url, char* outBuf, int outBufSize) {
    HINTERNET hInt = InternetOpenA("BootyCatalog/1.0", INTERNET_OPEN_TYPE_DIRECT, NULL, NULL, 0);
    if (!hInt) return -1;

    char host[256], path[512];
    memset(host, 0, sizeof(host));
    memset(path, 0, sizeof(path));

    /* Parse URL */
    const char* p = url;
    if (strncmp(p, "http://", 7) == 0) p += 7;
    else if (strncmp(p, "https://", 8) == 0) p += 8;

    const char* slash = strchr(p, '/');
    if (slash) {
        int hostLen = (int)(slash - p);
        if (hostLen > 255) hostLen = 255;
        strncpy(host, p, hostLen);
        strcpy(path, slash);
    } else {
        strncpy(host, p, 255);
        strcpy(path, "/");
    }

    DWORD flags = INTERNET_FLAG_RELOAD | INTERNET_FLAG_NO_CACHE_WRITE;
    if (strncmp(url, "https://", 8) == 0) flags |= INTERNET_FLAG_SECURE;

    HINTERNET hConnect = InternetConnectA(hInt, host, INTERNET_DEFAULT_HTTPS_PORT,
                                          NULL, NULL, INTERNET_SERVICE_HTTP, 0, 0);
    if (!hConnect) { InternetCloseHandle(hInt); return -1; }

    HINTERNET hReq = HttpOpenRequestA(hConnect, "GET", path, NULL, NULL, NULL, flags, 0);
    if (!hReq) { InternetCloseHandle(hConnect); InternetCloseHandle(hInt); return -1; }

    const char* ua = "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36";
    if (!HttpSendRequestA(hReq, ua, (DWORD)strlen(ua), NULL, 0)) {
        InternetCloseHandle(hReq); InternetCloseHandle(hConnect); InternetCloseHandle(hInt);
        return -1;
    }

    char* ptr = outBuf;
    char chunk[8192];
    DWORD bytesRead;
    int total = 0;

    while (total < outBufSize - 1024 && InternetReadFile(hReq, chunk, sizeof(chunk), &bytesRead)) {
        if (bytesRead == 0) break;
        if (total + (int)bytesRead >= outBufSize - 1) break;
        memcpy(ptr, chunk, bytesRead);
        ptr += bytesRead;
        total += (int)bytesRead;
    }
    *ptr = '\0';

    InternetCloseHandle(hReq);
    InternetCloseHandle(hConnect);
    InternetCloseHandle(hInt);
    return total;
}

/* Save downloaded JSON to disk, return 1 on success */
static int fetch_file_to_disk(const char* url, const char* filePath) {
    char buffer[65536];
    int n = fetch_remote(url, buffer, sizeof(buffer));
    if (n < 0) return 0;

    /* Simple HTTP header check - skip from "{", "[{" or "\n{" */
    while (n > 0 && (buffer[0] == '{' || buffer[0] == '[')) break;
    while (n > 0 && (buffer[0] == '\n' || buffer[0] == '\r' || buffer[0] == ' ' || buffer[0] == '{')) {
        if (buffer[0] == '{') break;
        n--; memmove(buffer, buffer + 1, n);
    }
    if (n <= 0) return 0;

    FILE* f = fopen(filePath, "wb");
    if (!f) return 0;
    fwrite(buffer, 1, n, f);
    fclose(f);
    return 1;
}

/* Extract version components from "major.minor.patch" string */
static void parse_version(const char* str, int* major, int* minor, int* patch) {
    *major = *minor = *patch = 0;
    if (!str) return;
    sscanf(str, "%d.%d.%d", major, minor, patch);
}

static void save_state(const char* version) {
    char cacheState[MAX_PATH];
    sprintf(cacheState, "%s\\%s", g_cacheDir, STATE_FILE);
    FILE* f = fopen(cacheState, "w");
    if (f) {
        fprintf(f, "{\"version\":\"%s\",\"lastCheck\":%ld}", version, (long)time(NULL));
        fclose(f);
    }
}

static int load_state(char* version, int versionSize) {
    char cacheState[MAX_PATH];
    sprintf(cacheState, "%s\\%s", g_cacheDir, STATE_FILE);
    FILE* f = fopen(cacheState, "r");
    if (!f) return 0;
    char buf[512];
    if (fgets(buf, sizeof(buf), f)) {
        fclose(f);
        /* Find "version":"x.x.x" */
        char* v = strstr(buf, "\"version\"");
        if (v) {
            v = strchr(v, ':');
            if (v) {
                v++;
                while (*v == ' ' || *v == '"') v++;
                int i = 0;
                while (v[i] && v[i] != '"' && i < 63) {
                    version[i] = v[i];
                    i++;
                }
                version[i] = '\0';
                return 1;
            }
        }
    }
    fclose(f);
    return 0;
}

/* Thread entry point */
static DWORD WINAPI update_thread(LPVOID param) {
    HWND hwnd = (HWND)param;
    int remoteMajor = 0, remoteMinor = 0, remotePatch = 0;
    int localMajor = 0, localMinor = 0, localPatch = 0;

    char buffer[16384];
    int n = fetch_remote(MANIFEST_URL, buffer, sizeof(buffer));

    if (n < 0) {
        const char* msg = "Network error checking for updates";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_NO_NET, (LPARAM)msg);
        return 1;
    }

    /* Parse manifest JSON: {"version":"1.2.3","gamesUrl":"https://..."} */
    char version[64] = {0};
    char gamesUrl[512] = {0};
    char* p = buffer;
    while (*p && n > 0) {
        char* key = strstr(p, "\"version\"");
        if (key) {
            key = strchr(key, ':');
            if (key) {
                key++;
                while (*key == ' ' || *key == '"') key++;
                int i = 0; while (key[i] && key[i] != '"' && i < 63) { version[i] = key[i]; i++; }
                version[i] = '\0';
            }
        }
        char* gurl = strstr(p, "\"gamesUrl\"");
        if (gurl) {
            gurl = strchr(gurl, ':');
            if (gurl) {
                gurl++;
                while (*gurl == ' ' || *gurl == '"') gurl++;
                int i = 0; while (gurl[i] && gurl[i] != '"' && i < 511) { gamesUrl[i] = gurl[i]; i++; }
                gamesUrl[i] = '\0';
            }
        }
        if (version[0] && gamesUrl[0]) break;
        p++; n--;
    }

    if (!version[0]) {
        const char* msg = "Update check failed (bad manifest)";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_PARSE_FAIL, (LPARAM)msg);
        return 1;
    }

    parse_version(version, &remoteMajor, &remoteMinor, &remotePatch);
    char localVer[64];
    load_state(localVer, sizeof(localVer));
    if (localVer[0]) {
        parse_version(localVer, &localMajor, &localMinor, &localPatch);
    }

    if (localMajor == remoteMajor && localMinor == remoteMinor && localPatch == remotePatch) {
        const char* msg = "Catalog up-to-date";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_SAME_VER, (LPARAM)msg);
        return 0;
    }

    get_cache_dir(g_cacheDir, sizeof(g_cacheDir));
    char cachePath[MAX_PATH];
    sprintf(cachePath, "%s\\%s", g_cacheDir, GAMES_CACHE_FILE);

    if (!gamesUrl[0]) {
        const char* msg = "No download URL in manifest";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_DL_FAIL, (LPARAM)msg);
        return 1;
    }

    /* Download the new games.json */
    int result = fetch_file_to_disk(gamesUrl, cachePath);
    if (!result) {
        const char* msg = "Download failed";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_DL_FAIL, (LPARAM)msg);
        return 1;
    }

    /* Load and validate the new catalog */
    FILE* f = fopen(cachePath, "rb");
    if (!f) {
        const char* msg = "Download OK but parse failed";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_PARSE_FAIL, (LPARAM)msg);
        return 1;
    }
    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* data = (char*)malloc(len + 1);
    fread(data, 1, len, f);
    fclose(f);
    data[len] = '\0';

    int newCount = parse_games_json(data, len);
    free(data);

    if (newCount <= 0) {
        const char* msg = "Downloaded catalog has no games";
        SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_PARSE_FAIL, (LPARAM)msg);
        return 1;
    }

    /* Success - save state and notify */
    save_state(version);
    SendMessageA(hwnd, WM_CATALOG_UPDATED, 1, 0);
    const char* msg = "Catalog updated - new games available!";
    SendMessageA(hwnd, WM_UPDATE_STATUS, UPD_OK, (LPARAM)msg);
    return 0;
}

/* ━━━ PUBLIC API ━━━ */

int start_update_check(HWND hwnd) {
    if (!hwnd) return 0;
    g_updateNotifyWnd = hwnd;
    DWORD tid;
    HANDLE h = CreateThread(NULL, 0, update_thread, hwnd, 0, &tid);
    if (h) {
        CloseHandle(h);
        return 1;
    }
    return 0;
}

void force_update_check(HWND hwnd) {
    if (hwnd) {
        start_update_check(hwnd);
    }
}

const char* get_cached_games_path(void) {
    if (g_cacheDir[0]) return g_cacheDir;
    get_cache_dir(g_cacheDir, sizeof(g_cacheDir));
    static char result[MAX_PATH];
    sprintf(result, "%s\\%s", g_cacheDir, GAMES_CACHE_FILE);
    return result;
}

int load_catalog_from_file(const char* filePath) {
    if (!filePath || !*filePath) return 0;
    FILE* f = fopen(filePath, "rb");
    if (!f) return -1;

    fseek(f, 0, SEEK_END);
    long len = ftell(f);
    fseek(f, 0, SEEK_SET);
    char* data = (char*)malloc(len + 1);
    if (!data) { fclose(f); return -1; }

    fread(data, 1, len, f);
    fclose(f);
    data[len] = '\0';

    int count = parse_games_json(data, len);
    free(data);
    return count;
}
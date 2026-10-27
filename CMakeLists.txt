cmake_minimum_required(VERSION 3.20)
project(BootyCatalog VERSION 1.0.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

# ━━━ Win32-specific ━━━
set(CMAKE_MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Release>:Release>")
add_definitions(-DUNICODE -D_UNICODE -DWIN32 -D_WINDOWS)

# ━━━ Find modules ━━━
find_package(ThreadPool 2 CONFIG QUIET)
find_package(nlohmann_json 3.11.3 CONFIG QUIET)

# ━━━ Resource compiler (RC) ━━━
# Windows RC file for embedding games.json, HTML, CSS, JS, icons
set(RESOURCES_DIR ${CMAKE_SOURCE_DIR}/resources)
set(RESC_FILE ${RESOURCES_DIR}/resources.rc)

# ━━━ HTML/JSON/CSS/JS resource generation ━━━
# Pre-embed all web assets as RCDATA resources
add_custom_command(
    OUTPUT ${RESOURCES_DIR}/embedded.h
    COMMAND python ${CMAKE_SOURCE_DIR}/tools/embed_resources.py
            ${RESOURCES_DIR}/games.bin
            ${RESOURCES_DIR}/html.bin
            ${RESOURCES_DIR}/css.bin
            ${RESOURCES_DIR}/js.bin
            ${RESOURCES_DIR}/jsdl.bin
            ${RESOURCES_DIR}/icon.bin
            ${RESOURCES_DIR}/tray.bin
    DEPENDS
        ${CMAKE_SOURCE_DIR}/data/games.json
        ${CMAKE_SOURCE_DIR}/index.html
        ${CMAKE_SOURCE_DIR}/styles/app.css
        ${CMAKE_SOURCE_DIR}/scripts/app.js
        ${CMAKE_SOURCE_DIR}/scripts/download.js
        ${RESOURCES_DIR}/booty.ico
        ${RESOURCES_DIR}/tray.ico
    COMMENT "Embedding resources into binary..."
)

add_custom_target(embed_resources DEPENDS ${RESOURCES_DIR}/embedded.h)

# ━━━ Main executable ━━━
add_executable(BootyCatalog
    WIN32
    ${RESOURCES_DIR}/resources.rc
    src/BootyCatalog.cpp
    src/HtmlRender.cpp
    src/WebBrowser.cpp
    src/DownloadManager.cpp
    src/TrayManager.cpp
    src/GridBrowser.cpp
    src/Theme.cpp
    src/Main.cpp
    src/embedded.cpp  # generated from embedded.h
)

add_dependencies(BootyCatalog embed_resources)

target_include_directories(BootyCatalog PRIVATE
    ${CMAKE_SOURCE_DIR}/include
    ${RESOURCES_DIR}
)

target_link_libraries(BootyCatalog PRIVATE
    comctl32
    shlwapi
    wininet
    ws2_32
    gdi32
    user32
    kernel32
)

target_compile_definitions(BootyCatalog PRIVATE
    UNICODE
    _UNICODE
    _CRT_SECURE_NO_WARNINGS
    WIN32_LEAN_AND_MEAN
)

# ━━━ MSVC optimizations ━━━
if(MSVC)
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /O2 /GL /Gy")
    set(CMAKE_CXX_FLAGS_RELEASE "${CMAKE_CXX_FLAGS_RELEASE} /std:c++20")
    set(CMAKE_EXE_LINKER_FLAGS_RELEASE "${CMAKE_EXE_LINKER_FLAGS_RELEASE} /LTCG /OPT:REF /OPT:IRREF")
endif()

# ━━━ Icon & manifest ━━━
set_property(TARGET BootyCatalog PROPERTY WIN32_EXECUTABLE TRUE)
set_property(TARGET BootyCatalog PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

# ━━━ Output ━━━
message(STATUS "Booty Catalog v${PROJECT_VERSION}")
message(STATUS "Output: ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/BootyCatalog.exe")

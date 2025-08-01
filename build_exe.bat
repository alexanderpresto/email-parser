@echo off
REM Build script for email-parser Windows executable

echo ===========================================
echo Email Parser Executable Build Script
echo ===========================================
echo.

REM Clean previous builds
if exist "build" (
    echo Cleaning previous build directory...
    rmdir /s /q build
)

if exist "dist" (
    echo Cleaning previous dist directory...
    rmdir /s /q dist
)

echo.
echo Building executable with PyInstaller...
echo.

REM Build the executable
pyinstaller email_parser.spec

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Build failed!
    exit /b %ERRORLEVEL%
)

echo.
echo ===========================================
echo Build completed successfully!
echo ===========================================
echo.
echo Executable location: dist\email-parser\email-parser.exe
echo.
echo To create a single-file portable version, uncomment the
echo exe_onefile section in email_parser.spec and rebuild.
echo.
@echo off
TITLE University Regulation RAG Assistant Launcher
COLOR 0B

echo ===================================================
echo   University Regulation RAG Assistant Launcher
echo ===================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH. Please install Python 3.11+.
    pause
    exit /b 1
)

REM Check if Node is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH. Please install Node.js 18+.
    pause
    exit /b 1
)

REM Set project root directory
set ROOT_DIR=%~dp0
cd /d "%ROOT_DIR%"

REM Create data folders if not present
if not exist "data\documents" mkdir "data\documents"
if not exist "data\index" mkdir "data\index"

REM Check .env file
if not exist "backend\.env" (
    echo [INFO] backend\.env not found. Copying from backend\.env.example...
    copy "backend\.env.example" "backend\.env"
    echo [NOTICE] Please edit backend\.env and add your NVIDIA_API_KEY.
)

echo [1/3] Starting FastAPI Backend on http://localhost:8000...
start "UniRAG Backend (FastAPI)" cmd /k "cd /d "%ROOT_DIR%" && if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait 3 seconds for backend to initialize
timeout /t 3 /nobreak >nul

echo [2/3] Starting React Frontend on http://localhost:5173...
start "UniRAG Frontend (Vite)" cmd /k "cd /d "%ROOT_DIR%frontend" && npm run dev"

REM Wait 3 seconds for Vite to initialize
timeout /t 3 /nobreak >nul

echo [3/3] Opening browser at http://localhost:5173...
start http://localhost:5173

echo.
echo ===================================================
echo   UniRAG Assistant is running!
echo   - Backend:  http://localhost:8000
echo   - Frontend: http://localhost:5173
echo   - API Docs: http://localhost:8000/docs
echo ===================================================
echo.
pause

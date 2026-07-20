@echo off
REM ============================================================
REM  AI Boot Camp - Day 7 environment setup (Windows)
REM  Creates ONE virtual environment and installs every package
REM  Day 7 needs (Streamlit, LiteLLM, python-dotenv, google-genai,
REM  pypdf) from requirements.txt.
REM  Usage: double-click, or run "install_ai_env.bat" in cmd.
REM ============================================================

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found. Install Python 3.10+ from https://www.python.org/downloads/
    echo         and tick "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo [1/3] Creating virtual environment .venv ...
python -m venv .venv
if errorlevel 1 (
    echo [ERROR] Could not create the virtual environment.
    pause
    exit /b 1
)

echo [2/3] Installing requirements.txt (Streamlit, LiteLLM, google-genai, ...) ...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Installation failed. Check your internet connection and retry.
    pause
    exit /b 1
)

echo [3/3] Verifying ...
streamlit --version
python -c "import litellm; print('litellm OK')"

echo.
echo ============================================================
echo  Python packages installed. ONE STEP LEFT before Topics
echo  01-04 will work: Ollama itself, plus the local models.
echo.
echo  1. Install Ollama (if you haven't already):
echo       https://ollama.com/download
echo.
echo  2. Check what models you already have:
echo       ollama list
echo.
echo  3. Pull a small local model if the list above is empty:
echo       ollama pull gemma3:4b
echo     (or: ollama pull llama3        -- either works with these docs)
echo.
echo  4. Ollama must be RUNNING before you use Topics 01-04:
echo       - The Ollama tray app (Windows) starts the server for you, or
echo       - run `ollama serve` manually in a terminal.
echo     It listens on http://localhost:11434 by default.
echo.
echo  Topics 03 (gemini_chatbot), 05, and Lab 02 use Google Gemini
echo  instead of Ollama - no local model needed, but you DO need a
echo  free API key from https://aistudio.google.com/ in each folder's
echo  .env file (GEMINI_API_KEY=...).
echo ============================================================
echo.
echo  To use this .venv from ANY Day 7 folder:
echo    .venv\Scripts\activate
echo    streamlit run app.py
echo ============================================================
pause

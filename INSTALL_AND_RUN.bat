@echo off
echo ============================================
echo   Kisan Sahayak - Install and Run
echo ============================================
echo.

echo [1/3] Installing required packages...
python -m pip install streamlit groq gtts SpeechRecognition audio-recorder-streamlit python-dotenv requests pandas --quiet

echo.
echo [2/3] Checking .env file...
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create a .env file with your GROQ_API_KEY
    echo Get free key at: https://console.groq.com
    pause
    exit
)

echo.
echo [3/3] Starting Kisan Sahayak...
echo Open browser at: http://localhost:8501
echo Press Ctrl+C to stop.
echo.
python -m streamlit run app.py

pause

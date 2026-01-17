@echo off
echo Starting Backend...
call venv\Scripts\activate || echo Venv not found, running globally
uvicorn app.main:app --reload
pause

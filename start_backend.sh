#!/bin/bash
echo "Starting Backend..."
if [ -d "venv" ]; then
    source venv/bin/activate
fi
uvicorn app.main:app --reload

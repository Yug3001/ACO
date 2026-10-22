@echo off
echo Starting PathWise Backend on http://127.0.0.1:8000
uvicorn api:app --reload --host 127.0.0.1 --port 8000

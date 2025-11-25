@echo off
REM

echo Starting API server with JWT authentication enabled...

REM
set ENABLE_JWT_AUTH=true
set DISABLE_DB=true

REM
python -m api.server

echo API server stopped.

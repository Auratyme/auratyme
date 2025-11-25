@echo off
REM Navigate to microservices folder
cd /d ../../microservices

REM Create .env files for each service
setlocal enabledelayedexpansion

set "services=auth\core auth\database broker gateway jobs\core jobs\database notifications\core notifications\database notifications\gateway schedules\core schedules\database schedules\gateway schedules-ai\core schedules-ai\database schedules-ai\gateway users\database users"

for %%s in (%services%) do (
  set "source=.\%%s\.env.example"
  set "dest=.\%%s\.env"
  
  if exist "!source!" (
    copy "!source!" "!dest!" /Y >nul
    echo Created .env for %%s
  ) else (
    echo WARNING: Missing .env.example for %%s
  )
)

echo.
echo Script completed!

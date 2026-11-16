@echo off
setlocal enabledelayedexpansion
title CrewAI Multi-Agent Market Intelligence System

:: Direct CLI argument dispatch
if /i "%~1"=="run" goto cli_run
if /i "%~1"=="test" goto cli_test
if /i "%~1"=="setup" goto cli_setup
if /i "%~1"=="install" goto cli_setup
if /i "%~1"=="open" goto cli_open
if /i "%~1"=="help" goto cli_help

:menu
cls
echo ===============================================================================
echo            CREWAI MULTI-AGENT MARKET RESEARCH ^& REPORT SYSTEM
echo ===============================================================================
echo   Status : Ready ^| Model: Gemini 3.1 Flash / OpenAI ^| Process: Hierarchical
echo ===============================================================================
echo.
echo   [1] Generate Market Report (Auto-Opens PDF on completion)
echo       - Runs Lead Researcher, Data Analyst ^& Content Writer agents
echo       - Computes Pandas financial statistics ^& compiles ReportLab A4 PDF
echo       - Automatically launches 'market_report.pdf' upon completion
echo.
echo   [2] Generate Report with Custom Topic
echo       - Prompts for custom sector/company query and executes full pipeline
echo       - Examples: "Semiconductor & AI Foundry Q3", "Cloud Hyperscaler Capex",
echo                   "Electric Vehicles ^& Battery Tech", "Cybersecurity SaaS Valuation"
echo.
echo   [3] Run Automated Test Suite (Pytest)
echo       - Verifies agent orchestration, Pandas math, benchmarks ^& PDF layout
echo.
echo   [4] System Setup ^& Dependency Verification
echo       - Checks Python environment and verifies dependencies
echo.
echo   [5] View Latest Generated PDF Report
echo.
echo   [0] Exit
echo.
echo ===============================================================================
set "choice="
set /p "choice=  Select option [1-5, or 0 to exit] (Default: 1): "

if "%choice%"=="" set choice=1
if "%choice%"=="1" goto op_default
if "%choice%"=="2" goto op_custom
if "%choice%"=="3" goto op_test
if "%choice%"=="4" goto op_setup
if "%choice%"=="5" goto op_open
if "%choice%"=="0" goto op_exit
goto menu

:op_default
cls
echo.
echo ===============================================================================
echo   EXECUTING MULTI-AGENT MARKET RESEARCH PIPELINE
echo ===============================================================================
echo   Query: "Tech Sector Q3 Analysis"
echo -------------------------------------------------------------------------------
python main.py --query "Tech Sector Q3 Analysis"
echo.
echo [*] Opening generated PDF report in your default viewer...
if exist "output\market_report.pdf" (
    start "" "output\market_report.pdf"
) else if exist "market_report.pdf" (
    start "" "market_report.pdf"
)
echo.
pause
goto menu

:op_custom
cls
echo.
echo ===============================================================================
echo   CUSTOM MARKET RESEARCH QUERY
echo ===============================================================================
echo   Examples:
echo     1. Semiconductor ^& AI Hardware Infrastructure
echo     2. Cloud Hyperscaler Growth ^& Enterprise Capex
echo     3. Electric Vehicles ^& Clean Energy Multiples
echo     4. Global Enterprise Software ^& SaaS Margins
echo -------------------------------------------------------------------------------
set "custom_query="
set /p "custom_query=  Enter research topic (Default: Tech Sector Q3 Analysis): "
if "!custom_query!"=="" set "custom_query=Tech Sector Q3 Analysis"
echo.
echo [*] Executing pipeline for: "!custom_query!"...
python main.py --query "!custom_query!"
echo.
echo [*] Opening generated PDF report in your default viewer...
if exist "output\market_report.pdf" (
    start "" "output\market_report.pdf"
) else if exist "market_report.pdf" (
    start "" "market_report.pdf"
)
echo.
pause
goto menu

:op_test
cls
echo.
echo ===============================================================================
echo   RUNNING AUTOMATED TEST SUITE (PYTEST)
echo ===============================================================================
python -m pytest -v
echo.
echo ===============================================================================
pause
goto menu

:op_setup
cls
echo.
echo ===============================================================================
echo   SYSTEM ENVIRONMENT ^& DEPENDENCIES SETUP
echo ===============================================================================
echo [*] Checking Python installation...
python --version
echo.
echo [*] Verifying and installing dependencies...
pip install -r requirements.txt
pip install google-genai
echo.
echo [*] Setup complete.
pause
goto menu

:op_open
cls
echo.
if exist "output\market_report.pdf" (
    echo [*] Opening output\market_report.pdf...
    start "" "output\market_report.pdf"
) else if exist "market_report.pdf" (
    echo [*] Opening market_report.pdf...
    start "" "market_report.pdf"
) else (
    echo [!] No report found yet. Run Option [1] first to generate a report.
)
echo.
pause
goto menu

:cli_run
shift
set "query=%~1"
if "%query%"=="" set "query=Tech Sector Q3 Analysis"
python main.py --query "%query%"
if exist "output\market_report.pdf" start "" "output\market_report.pdf"
goto op_exit

:cli_test
python -m pytest -v
goto op_exit

:cli_setup
pip install -r requirements.txt
pip install google-genai
goto op_exit

:cli_open
if exist "output\market_report.pdf" (
    start "" "output\market_report.pdf"
) else if exist "market_report.pdf" (
    start "" "market_report.pdf"
) else (
    echo [!] No report found.
)
goto op_exit

:cli_help
echo.
echo ===============================================================================
echo   CrewAI Market Research CLI Runner - Command Reference ^& Examples
echo ===============================================================================
echo   Interactive Mode:
echo     run.bat
echo.
echo   Direct Command Examples:
echo     run.bat run                                (Runs default Tech Sector analysis)
echo     run.bat run "Semiconductor & AI Hardware"  (Runs with custom query)
echo     run.bat run "Cloud Hyperscalers Capex"     (Runs with cloud capex topic)
echo     run.bat test                               (Runs 9 automated pytest tests)
echo     run.bat setup                              (Installs all dependencies)
echo     run.bat open                               (Opens market_report.pdf)
echo ===============================================================================
goto op_exit

:op_exit
exit /b 0

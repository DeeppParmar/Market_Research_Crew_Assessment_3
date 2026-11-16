@echo off
setlocal enabledelayedexpansion

if "%~1"=="" goto menu
if /i "%~1"=="run" goto run_app
if /i "%~1"=="test" goto run_test
if /i "%~1"=="install" goto install_deps
if /i "%~1"=="open" goto open_pdf
if /i "%~1"=="help" goto show_help
goto invalid_arg

:menu
cls
echo ===========================================================================
echo   CREWAI MARKET RESEARCH ^& REPORT GENERATOR - CONTROL PANEL
echo ===========================================================================
echo   [1] Run Multi-Agent Workflow (Default: Tech Sector Q3 Analysis)
echo   [2] Run Multi-Agent Workflow with Custom Query
echo   [3] Run Automated Pytest Test Suite
echo   [4] Install / Verify Dependencies (requirements.txt)
echo   [5] Open Generated PDF Report (market_report.pdf)
echo   [6] Exit
echo ===========================================================================
set /p choice="Select an option [1-6]: "

if "%choice%"=="1" goto run_default
if "%choice%"=="2" goto run_custom
if "%choice%"=="3" goto run_test
if "%choice%"=="4" goto install_deps
if "%choice%"=="5" goto open_pdf
if "%choice%"=="6" goto end
goto menu

:run_default
echo.
echo [*] Executing Multi-Agent Market Research Workflow...
python main.py --query "Tech Sector Q3 Analysis"
echo.
echo [*] Done. Output PDF generated at output/market_report.pdf
pause
goto menu

:run_custom
echo.
set /p custom_query="Enter your market query: "
if "!custom_query!"=="" set custom_query=Tech Sector Q3 Analysis
echo [*] Executing Multi-Agent Market Research for: "!custom_query!"...
python main.py --query "!custom_query!"
echo.
echo [*] Done. Output PDF generated at output/market_report.pdf
pause
goto menu

:run_app
shift
set "query=%~1"
if "%query%"=="" set "query=Tech Sector Q3 Analysis"
echo [*] Executing: python main.py --query "%query%"
python main.py --query "%query%"
goto end

:run_test
echo.
echo [*] Running automated test suite (pytest)...
python -m pytest -v
goto end

:install_deps
echo.
echo [*] Installing dependencies from requirements.txt...
pip install -r requirements.txt
pip install google-genai
goto end

:open_pdf
echo.
if exist "output\market_report.pdf" (
    echo [*] Opening output\market_report.pdf...
    start "" "output\market_report.pdf"
) else if exist "market_report.pdf" (
    echo [*] Opening market_report.pdf...
    start "" "market_report.pdf"
) else (
    echo [!] No generated PDF report found. Please run the workflow first.
)
goto end

:show_help
echo.
echo ===========================================================================
echo   CrewAI Market Research CLI Runner
echo ===========================================================================
echo   run.bat                 Opens interactive menu
echo   run.bat run [query]     Runs workflow (e.g. run.bat run "Cloud AI Q3")
echo   run.bat test            Runs automated test suite (pytest)
echo   run.bat install         Installs all required dependencies
echo   run.bat open            Opens generated PDF report in default viewer
echo ===========================================================================
goto end

:invalid_arg
echo [!] Unknown option: %1
goto show_help

:end

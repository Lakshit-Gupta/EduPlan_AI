@echo off
echo EduPlan AI - Lesson Plan Generation System
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in the PATH
    echo Please install Python 3.9 or later and try again.
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
pip show qdrant-client >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error installing dependencies. Please check requirements.txt
        pause
        exit /b 1
    )
)

echo.
echo Select an option:
echo 1. Start API server
echo 2. Ingest sample documents
echo 3. Generate a sample lesson plan
echo 4. Exit
echo.

set /p option="Enter your choice (1-4): "

if "%option%"=="1" (
    echo Starting API server...
    python src/main.py api
) else if "%option%"=="2" (
    echo Ingesting sample documents...
    python src/main.py ingest data/sample_documents
    pause
) else if "%option%"=="3" (
    set /p query="Enter lesson plan query: "
    set /p class="Enter class filter (1-12, or leave empty): "
    set /p subject="Enter subject filter (or leave empty): "
    
    if not "%class%"=="" if not "%subject%"=="" (
        echo Generating lesson plan...
        python src/main.py generate "%query%" --class-filter %class% --subject-filter %subject%
    ) else if not "%class%"=="" (
        echo Generating lesson plan...
        python src/main.py generate "%query%" --class-filter %class%
    ) else (
        echo Generating lesson plan...
        python src/main.py generate "%query%"
    )
    pause
) else if "%option%"=="4" (
    echo Exiting...
    exit /b 0
) else (
    echo Invalid option.
    pause
)

exit /b 0

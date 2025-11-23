@echo off

:: Set the script directory
set SCRIPT_DIR=%~dp0

:: Path to your Miniconda installation
set CONDA_PATH=%SCRIPT_DIR%miniconda

:: Initialize Conda for this script session only
call "%CONDA_PATH%\Scripts\activate.bat"

:: Activate the conda environment
call conda activate crewai_env || (
    echo Failed to activate conda environment
    exit /b 1
)

:: Disable TLS/SSL verification for runtime
set PYTHONHTTPSVERIFY=0
set REQUESTS_CA_BUNDLE=
set CURL_CA_BUNDLE=
set SSL_CERT_FILE=

cd %SCRIPT_DIR%

:: Run the Streamlit application
streamlit run app/app.py --server.headless True

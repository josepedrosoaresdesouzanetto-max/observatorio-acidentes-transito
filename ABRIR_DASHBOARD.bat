@echo off
cd /d "%~dp0"
echo Abrindo o dashboard do Observatorio de Acidentes de Transito...
echo.
python -m streamlit run dashboard/app.py
if errorlevel 1 (
    echo.
    echo Nao foi possivel abrir o dashboard.
    echo Verifique se as dependencias foram instaladas com:
    echo pip install -r requirements.txt
    echo.
    pause
)

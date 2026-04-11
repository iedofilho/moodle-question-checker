@echo off
echo ==============================================
echo Iniciando Moodle Question Checker
echo ==============================================

:: Verifica se a venv existe
if not exist "venv" (
    echo [INFO] Primeira vez! Preparando motor Python...
    python -m venv venv
)

:: Ativa o ambiente
call venv\Scripts\activate

:: Instala dependencias apenas na primeira execucao para ganhar velocidade brutal
if not exist "venv\.installed" (
    echo [INFO] Baixando recursos (Isto so ocorre na primeira execucao. Aguarde...)
    pip install -r requirements.txt > nul 2>&1
    playwright install chromium > nul 2>&1
    echo Instalado > "venv\.installed"
)

:: Roda o script imediatamente
python run_check.py

echo.
echo Processo finalizado!
pause

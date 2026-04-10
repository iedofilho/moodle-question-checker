@echo off
echo ==============================================
echo Iniciando Moodle Question Checker
echo ==============================================

:: Verifica se a venv existe
if not exist "venv" (
    echo [INFO] Criando ambiente virtual...
    python -m venv venv
)

:: Ativa o ambiente
call venv\Scripts\activate

:: Instala dependencias caso falte algo
echo [INFO] Verificando dependencias...
pip install -r requirements.txt > nul 2>&1
playwright install chromium > nul 2>&1

:: Roda o script
echo [INFO] Executando validacao...
python run_check.py

echo.
echo Processo finalizado!
pause

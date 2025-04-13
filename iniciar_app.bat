@echo off
cd /d "%~dp0"
call venv\Scripts\activate

echo Haciendo makemigrations...
python manage.py makemigrations

echo Aplicando migrate...
python manage.py migrate

start http://127.0.0.1:8000
python manage.py runserver

pause

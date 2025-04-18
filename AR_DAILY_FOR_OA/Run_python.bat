@echo off

cd /D "%~dp0"
pipenv install & pipenv run python main.py
pause

@echo off
rem Audio 2 MP3 launcher - version 1.1.1 (2026-09-27)
chcp 65001 >nul
cd /d "%~dp0"
py convert.py
pause

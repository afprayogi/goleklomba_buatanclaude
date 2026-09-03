@echo off
REM Preview lomba baru yang AKAN dikirim, tanpa benar-benar mengirim apa pun.
cd /d "%~dp0"
python kirim_info_lomba.py --dry-run
pause

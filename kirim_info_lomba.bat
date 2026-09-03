@echo off
REM Kirim info lomba baru ke WhatsApp (beneran mengirim, bukan preview).
REM Pastikan WhatsApp gateway di wa_config.yaml sudah jalan sebelum klik ini.
cd /d "%~dp0"
python kirim_info_lomba.py
pause

@echo off
rem echo Congratulations! Your first batch file was executed successfully.
rem pause

rem OUTPUT FILES
SET EXEFILE=radgame.exe
SET ZIPFILE=radgame-py.zip

rem PRECLEAN
if exist %EXEFILE% (
  del %EXEFILE%
)
if exist %ZIPFILE% (
  del %ZIPFILE%
)

rem BUILD
python -m PyInstaller --onefile -windowed --name=radgame --icon=radgame.ico radgamegui.py

rem POST CLEAN
copy dist\%EXEFILE% .
rmdir /S /Q __pycache__ build dist
del radgame.spec

rem ZIP
"C:\Program Files\7-Zip\7z" a %ZIPFILE% ..\radgame

rem BACKUP
COPY /Y %ZIPFILE% C:\Users\kavi\Dropbox\avik\__backup__\python\radgame

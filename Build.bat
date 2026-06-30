@echo off
rem Build script: packages the Tkinter GUI into a standalone Windows executable.
rem Requires PyInstaller (pip install pyinstaller) and Python on PATH.

SET SRC=src
SET EXEFILE=radgame.exe
SET DIST=dist

rem PRECLEAN
if exist %DIST%\%EXEFILE% (
    del %DIST%\%EXEFILE%
)

rem BUILD
cd %SRC%
python -m PyInstaller --onefile --windowed --name=radgame --icon=radgame.ico radgamegui.py
cd ..

rem MOVE OUTPUT TO dist/
if not exist %DIST% mkdir %DIST%
move /Y %SRC%\dist\%EXEFILE% %DIST%\%EXEFILE%

rem CLEANUP
if exist %SRC%\__pycache__ rmdir /S /Q %SRC%\__pycache__
if exist %SRC%\build rmdir /S /Q %SRC%\build
if exist %SRC%\dist rmdir /S /Q %SRC%\dist
if exist %SRC%\radgame.spec del %SRC%\radgame.spec

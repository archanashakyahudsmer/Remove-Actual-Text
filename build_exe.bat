@echo off
REM Run from the project root (the folder that contains app\, frontend\, launcher.py)
python -m pip install --upgrade pip
pip install -r requirements.txt pyinstaller

pyinstaller --noconfirm --clean --onefile --console ^
  --name PDFSpanRemover ^
  --add-data "frontend;frontend" ^
  --collect-submodules uvicorn ^
  --collect-submodules multipart ^
  --collect-submodules python_multipart ^
  --collect-all pymupdf ^
  --hidden-import starlette.routing ^
  --hidden-import starlette.middleware ^
  --hidden-import starlette.staticfiles ^
  --hidden-import starlette.responses ^
  --hidden-import starlette.background ^
  --hidden-import anyio ^
  --hidden-import anyio._backends._asyncio ^
  --hidden-import anyio._backends._trio ^
  launcher.py

echo.
echo Done. Your exe is at dist\PDFSpanRemover.exe
pause

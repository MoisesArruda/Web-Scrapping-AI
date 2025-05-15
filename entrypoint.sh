#!/usr/bin/env sh
set -e

echo "Baixando arquivos necessários..."
python main.py download-files

echo "Iniciando servidor FastAPI no uvicorn..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8080 
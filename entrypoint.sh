#!/usr/bin/env sh
set -e

echo "Verificando variável de ambiente PORT..."
PORT=${PORT:-8080}
echo "Usando porta: $PORT"

echo "Iniciando Streamlit diretamente na porta $PORT..."
exec streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
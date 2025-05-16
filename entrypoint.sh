#!/usr/bin/env sh
#!/usr/bin/env sh
set -e

echo "Verificando variável de ambiente PORT..."
PORT=${PORT:-8080}
echo "Usando porta: $PORT"

echo "Iniciando servidor FastAPI no uvicorn..."
exec python -m uvicorn main:app --host 0.0.0.0 --port $PORT
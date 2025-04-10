echo "Iniciando o backend..."
python -m app.api.routes &

# Aguarda alguns segundos para garantir que o backend está rodando
sleep 2

# Inicia o frontend
echo "Iniciando o frontend..."
streamlit run main.py --server.address 0.0.0.0 --server.port 8501
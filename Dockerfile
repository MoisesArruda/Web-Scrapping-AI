FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Expõe as portas necessárias
EXPOSE 8000 8501

# Comando para rodar o Streamlit
# CMD ["streamlit", "run", "main.py", "--server.address", "0.0.0.0", "--server.port", "8501"]
# O CMD não permite executar dois scripts, um para a API do backend e outra para o front
CMD ["sh", "start.sh"]

# buildar a imagem 
# podman build -t frontend .

# rodar a imagem
# podman run -p 8501:8501 frontend


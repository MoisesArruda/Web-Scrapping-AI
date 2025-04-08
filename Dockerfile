FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "frontend.py", "--server.address", "0.0.0.0", "--server.port", "8501"]


# buildar a imagem 
# podman build -t frontend .

# rodar a imagem
# podman run -p 8501:8501 frontend


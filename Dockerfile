FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

# Expõe as portas necessárias
EXPOSE 8080

# Comando para rodar o Streamlit



# Como rodar

Essa solução está conectando a API Backend com o Frontend, para roda-la é necessário primeiramente ativar o módulo da API de back

```bash
python -m app.api.routes
```

Após, para iniciar o frontend, arrastar o script até a pasta raiz do projeto

```bash
streamlit run frontend.py
```

Rodar o main.py, não esquecer de retornar o frontend para a pasta dele

```bash
streamlit run main.py
```

## Container

O CMD do dockerfile não permite rodar dois comandos, para isso criamos o arquivo **start.sh** com os comandos necessários para rodar

```bash
podman build -t api_frontend .
```

Para conseguir acessar o back e o front em http://localhost:8000 e http://localhost:8501

```bash
podman run -p 8000:8000 -p 8501:8501 api_frontend
```

Para acessar apenas o front

```bash
podman run -p 8501:8501 api_frontend
```
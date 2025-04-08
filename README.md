# Frontend

Consigo rodar a API, mas não estou conectando ela entre frontend e backend.


1. buildar a imagem 

```bash
podman build -t frontend .
```

2. rodar a imagem

```bash 
podman run -p 8501:8501 frontend
```
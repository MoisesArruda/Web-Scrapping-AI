from fastapi import APIRouter, HTTPException, FastAPI
from pydantic import BaseModel
from app.backend.evaluator import StartupEvaluator

# Criar a aplicação FastAPI
app = FastAPI(
    title="Avaliador de Startups",
    description="API para análise e avaliação de startups baseado em conteúdo web",
    version="1.0.0"
)

# Criar o router
router = APIRouter()
evaluator = StartupEvaluator()

@router.get("/")
async def root():
    """
    Rota inicial com informações básicas da API.
    """
    return {
        "mensagem": "Bem-vindo à API de Avaliação de Startups",
        "endpoints_disponíveis": {
            "POST /evaluate": "Avalia uma startup (envie URL no corpo JSON)",
            "GET /evaluate/{url}": "Avalia uma startup (URL direto no caminho)",
            "GET /docs": "Documentação interativa da API"
        },
        "exemplo_de_uso": "http://localhost:8000/evaluate/https://www.cleverdash.ai"
    }

class Query(BaseModel):
    url: str

@router.post("/evaluate")
async def evaluate_agent(query: Query):
    """
    Avalia uma startup com base na URL fornecida.
    """
    try:
        result = evaluator.evaluate(query.url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/evaluate/{url:path}")
async def evaluate_agent_path(url: str):
    """
    Endpoint GET para teste via navegador.
    """
    try:
        result = evaluator.evaluate(url)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Incluir o router na aplicação
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    print("Iniciando servidor na porta 8000...")
    print("Acesse a documentação em: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)

    # Colar no navegador: http://localhost:8000/evaluate/https://www.cleverdash.ai/

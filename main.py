from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, HttpUrl
import requests
from dotenv import load_dotenv
import os
import io
import re
from typing import List, Optional
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from bs4 import BeautifulSoup
from functools import lru_cache

# Load environment variables (ensure .env contains OPENAI_API_KEY)
load_dotenv()

llm = ChatGroq(model="qwen-2.5-32b", temperature=0.7)

app = FastAPI(
    title="Avaliador de Startups",
    description="API para análise e avaliação de startups baseado em conteúdo web",
    version="1.0.0"
)

# Adicionando rota raiz
@app.get("/")
async def root():
    return {"message": "Bem-vindo à API de Avaliação de Startups"}

@lru_cache(maxsize=100)
def fetch_website_content(url: str) -> str:
    """
    Extrai o conteúdo textual de uma página web através de uma requisição HTTP com o método GET.
    Inclui cache para evitar requisições repetidas.

    Parametros:
        url (str): A URL da página web a ser extraída.

    Retorna:
        str: O conteúdo textual da página web.
    """
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text(separator=" ", strip=True)
            return text
        return f"Error: Unable to fetch website content (status {response.status_code})"
    except Exception as e:
        return f"Exception: {str(e)}"

class State(TypedDict):
    url: str
    descriptor: str
    market_trends: str
    rating: int
    final_answer: str
    enough: bool
    iterations: int
    thoughts: List[str]

# Node 1: Generate a one-line descriptor from website content.
def step_descriptor(state: State) -> dict:
    content = fetch_website_content(state["url"])
    if content.startswith("Error") or content.startswith("Exception"):
        return {"descriptor": content}
    snippet = content[:1000]
    prompt = (
        f"Forneça um descritor conciso de uma linha resumindo o conteúdo do site.\n\n"
        f"Trecho do conteúdo:\n{snippet}"
    )
    response_msg = llm.invoke(prompt)
    descriptor = response_msg.content  # Extract text content.
    return {"descriptor": descriptor.strip()}

# Node 2: Decide if enough information is available.
def step_decision(state: State) -> dict:
    if state["iterations"] >= 3:
        return {"enough": True}
    prompt = (
        f"Com base na seguinte descrição do site:\n'{state['descriptor']}'\n"
        f"e os insights adicionais até agora: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
        "Você tem informações suficientes para avaliar esta ideia de negócio de forma confiável? "
        "Responda com 'sim' ou 'não'."
    )
    decision_msg = llm.invoke(prompt)
    decision_text = decision_msg.content
    enough = "sim" in decision_text.lower()
    return {"enough": enough}

# Node 3: Think more – generate an additional insight and update market trends.
def step_think_more(state: State) -> dict:
    new_iter = state["iterations"] + 1
    prompt_insight = (
        f"Descrição do site: '{state['descriptor']}'.\n"
        f"Insights existentes: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}.\n"
        "Qual é um insight ou fator adicional que deve ser considerado para avaliar esta ideia de negócio? "
        "Responda em uma frase concisa."
    )
    insight_msg = llm.invoke(prompt_insight)
    new_thought = insight_msg.content.strip()
    updated_thoughts = state["thoughts"] + [new_thought]
    prompt_trends = (
        f"Com base na descrição do site '{state['descriptor']}' e no novo insight '{new_thought}', "
        "forneça um resumo atualizado e breve das tendências de mercado relevantes em uma frase."
    )
    trends_msg = llm.invoke(prompt_trends)
    new_trends = trends_msg.content.strip()
    return {"iterations": new_iter, "thoughts": updated_thoughts, "market_trends": new_trends}

# Node 4: Finalize the answer.
def step_finalize(state: State) -> dict:
    prompt = (
        f"Usando a descrição do site:\n'{state['descriptor']}'\n"
        f"e os seguintes insights adicionais: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
        f"com resumo das tendências de mercado: '{state['market_trends']}'\n"
        "Forneça uma avaliação final do negócio em 3-5 linhas e classifique a ideia de negócio em uma escala de 1 (ruim) a 10 (excelente). "
        "Formate sua resposta como: 'Resumo Final: ...; Avaliação: X'"
    )
    final_msg = llm.invoke(prompt)
    final = final_msg.content.strip()
    match = re.search(r'Avaliação:\s*(\d+)', final)
    rating = int(match.group(1)) if match else 0
    return {"final_answer": final, "rating": rating}

# Router function: after the decision node, decide whether to loop or finalize.
def decision_router(state: State):
    if state.get("enough", False):
        return "step_finalize"
    return "step_think_more"

# Build the cyclic graph.
graph_builder = StateGraph(State)
graph_builder.add_node(step_descriptor)
graph_builder.add_node(step_decision)
graph_builder.add_node(step_think_more)
graph_builder.add_node(step_finalize)

graph_builder.add_edge(START, "step_descriptor")
graph_builder.add_edge("step_descriptor", "step_decision")
graph_builder.add_conditional_edges("step_decision", decision_router, {"step_think_more": "step_think_more", "step_finalize": "step_finalize"})
graph_builder.add_edge("step_think_more", "step_decision")
graph_builder.add_edge("step_finalize", END)

graph = graph_builder.compile()



class Query(BaseModel):
    url: str

@app.post("/evaluate")
async def evaluate_agent(query: Query):
    initial_state: State = {
        "url": query.url,
        "descriptor": "",
        "market_trends": "",
        "rating": 0,
        "final_answer": "",
        "enough": False,
        "iterations": 0,
        "thoughts": [],
    }
    result = graph.invoke(initial_state)
    return result

@app.get("/visualize")
async def visualize():
    img_bytes = graph.get_graph().draw_mermaid_png()
    return StreamingResponse(io.BytesIO(img_bytes), media_type="image/png")

if __name__ == "__main__":
    
    #print(fetch_website_content("https://www.cleverdash.ai/"))
    # print(fetch_website_content("https://ia.adapta.org/"))
    # https://lovable.dev

    import uvicorn
    uvicorn.run(app)#, reload=True)


import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
from typing_extensions import TypedDict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from pydantic import BaseModel
from functools import lru_cache

class State(TypedDict):
    url: str
    descriptor: str
    market_trends: str
    rating: int
    final_answer: str
    enough: bool
    iterations: int
    thoughts: List[str]

class StartupEvaluator:
    """
    Avaliador de startups baseado em conteúdo web.
    Usa um grafo de processamento para analisar websites e gerar uma avaliação.
    """
    
    def __init__(self, model="qwen-2.5-32b", temperature=0.7):
        """
        Inicializa o avaliador com o modelo especificado.
        
        Args:
            model: O modelo LLM a ser usado (padrão: "qwen-2.5-32b")
            temperature: Temperatura para geração de texto (padrão: 0.7)
        """
        self.llm = ChatGroq(model=model, temperature=temperature)
        self.graph = self._build_graph()
        
    @lru_cache(maxsize=100)
    def fetch_website_content(self, url: str) -> str:
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
    
    def _step_descriptor(self, state: State) -> dict:
        """
        Gera um descritor de uma linha a partir do conteúdo do site.
        """
        content = self.fetch_website_content(state["url"])
        if content.startswith("Error") or content.startswith("Exception"):
            return {"descriptor": content}
        snippet = content[:1000]
        prompt = (
            f"Forneça um descritor conciso de uma linha resumindo o conteúdo do site.\n\n"
            f"Trecho do conteúdo:\n{snippet}"
        )
        response_msg = self.llm.invoke(prompt)
        descriptor = response_msg.content  # Extract text content.
        return {"descriptor": descriptor.strip()}

    def _step_decision(self, state: State) -> dict:
        """
        Decide se temos informações suficientes para avaliação.
        """
        if state["iterations"] >= 3:
            return {"enough": True}
        prompt = (
            f"Com base na seguinte descrição do site:\n'{state['descriptor']}'\n"
            f"e os insights adicionais até agora: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
            "Você tem informações suficientes para avaliar esta ideia de negócio de forma confiável? "
            "Responda com 'sim' ou 'não'."
        )
        decision_msg = self.llm.invoke(prompt)
        decision_text = decision_msg.content
        enough = "sim" in decision_text.lower()
        return {"enough": enough}

    def _step_think_more(self, state: State) -> dict:
        """
        Gera um insight adicional e atualiza as tendências de mercado.
        """
        new_iter = state["iterations"] + 1
        prompt_insight = (
            f"Descrição do site: '{state['descriptor']}'.\n"
            f"Insights existentes: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}.\n"
            "Qual é um insight ou fator adicional que deve ser considerado para avaliar esta ideia de negócio? "
            "Responda em uma frase concisa."
        )
        insight_msg = self.llm.invoke(prompt_insight)
        new_thought = insight_msg.content.strip()
        updated_thoughts = state["thoughts"] + [new_thought]
        prompt_trends = (
            f"Com base na descrição do site '{state['descriptor']}' e no novo insight '{new_thought}', "
            "forneça um resumo atualizado e breve das tendências de mercado relevantes em uma frase."
        )
        trends_msg = self.llm.invoke(prompt_trends)
        new_trends = trends_msg.content.strip()
        return {"iterations": new_iter, "thoughts": updated_thoughts, "market_trends": new_trends}

    def _step_finalize(self, state: State) -> dict:
        """
        Finaliza a avaliação e atribui uma nota.
        """
        prompt = (
            f"Usando a descrição do site:\n'{state['descriptor']}'\n"
            f"e os seguintes insights adicionais: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
            f"com resumo das tendências de mercado: '{state['market_trends']}'\n"
            "Forneça uma avaliação final do negócio em 3-5 linhas e classifique a ideia de negócio em uma escala de 1 (ruim) a 10 (excelente). "
            "Formate sua resposta como: 'Resumo Final: ...; Avaliação: X'"
        )
        final_msg = self.llm.invoke(prompt)
        final = final_msg.content.strip()
        match = re.search(r'Avaliação:\s*(\d+)', final)
        rating = int(match.group(1)) if match else 0
        return {"final_answer": final, "rating": rating}

    def _decision_router(self, state: State):
        """
        Função de roteamento após o nó de decisão.
        """
        if state.get("enough", False):
            return "step_finalize"
        return "step_think_more"

    def _build_graph(self):
        """
        Constrói o grafo de processamento para avaliação.
        """
        graph_builder = StateGraph(State)
        
        # Adiciona os nós
        graph_builder.add_node("step_descriptor", self._step_descriptor)
        graph_builder.add_node("step_decision", self._step_decision)
        graph_builder.add_node("step_think_more", self._step_think_more)
        graph_builder.add_node("step_finalize", self._step_finalize)
        
        # Configura as transições
        graph_builder.add_edge(START, "step_descriptor")
        graph_builder.add_edge("step_descriptor", "step_decision")
        graph_builder.add_conditional_edges(
            "step_decision", 
            self._decision_router, 
            {"step_think_more": "step_think_more", "step_finalize": "step_finalize"}
        )
        graph_builder.add_edge("step_think_more", "step_decision")
        graph_builder.add_edge("step_finalize", END)
        
        # Compila e retorna
        return graph_builder.compile()
        
    def evaluate(self, url: str) -> Dict[str, Any]:
        """
        Avalia uma startup com base na URL do seu site.
        
        Args:
            url: A URL do site da startup
            
        Returns:
            Um dicionário com os resultados da avaliação
        """
        initial_state: State = {
            "url": url,
            "descriptor": "",
            "market_trends": "",
            "rating": 0,
            "final_answer": "",
            "enough": False,
            "iterations": 0,
            "thoughts": [],
        }
        result = self.graph.invoke(initial_state)
        return result 
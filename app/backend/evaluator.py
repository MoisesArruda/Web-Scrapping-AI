from typing import List, Dict
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from .web_scraper import fetch_website_content
import os
from dotenv import load_dotenv
from typing_extensions import TypedDict

# Carrega variáveis de ambiente
load_dotenv()

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
    def __init__(self):
        self.llm = ChatGroq(
            model=os.getenv("LLM_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct"),
            temperature=float(os.getenv("LLM_TEMPERATURE", "0.7"))
        )
        self.graph = self._build_graph()

    def evaluate(self, url: str) -> Dict:
        """
        Avalia uma startup com base na URL fornecida.
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
        return self.graph.invoke(initial_state)

    def _build_graph(self) -> StateGraph:
        """
        Constrói o grafo de avaliação.
        """
        graph_builder = StateGraph(State)
        
        # Adiciona os nós
        graph_builder.add_node("step_descriptor", self._step_descriptor)
        graph_builder.add_node("step_decision", self._step_decision)
        graph_builder.add_node("step_think_more", self._step_think_more)
        graph_builder.add_node("step_finalize", self._step_finalize)

        # Configura as conexões
        graph_builder.add_edge(START, "step_descriptor")
        graph_builder.add_edge("step_descriptor", "step_decision")
        graph_builder.add_conditional_edges(
            "step_decision",
            self._decision_router,
            {
                "step_think_more": "step_think_more",
                "step_finalize": "step_finalize"
            }
        )
        graph_builder.add_edge("step_think_more", "step_decision")
        graph_builder.add_edge("step_finalize", END)

        return graph_builder.compile()

    def _step_descriptor(self, state: Dict) -> Dict:
        content = fetch_website_content(state["url"])
        if content.startswith("Error") or content.startswith("Exception"):
            return {"descriptor": content}
        
        snippet = content[:1000]
        prompt = (
            f"Forneça uma descrição concisa de uma linha resumindo o conteúdo do site.\n\n"
            f"Trecho do conteúdo:\n{snippet}"
        )
        response_msg = self.llm.invoke(prompt)
        return {"descriptor": response_msg.content.strip()}

    def _step_decision(self, state: Dict) -> Dict:
        if state["iterations"] >= 3:
            return {"enough": True}
        prompt = (
            f"Com base na seguinte descrição do site:\n'{state['descriptor']}'\n"
            f"e nos insights adicionais até agora: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
            "Temos informações suficientes para avaliar esta ideia de negócio de forma confiável? "
            "Responda com 'sim' ou 'não'."
        )
        decision_msg = self.llm.invoke(prompt)
        decision_text = decision_msg.content
        enough = "sim" in decision_text.lower()
        return {"enough": enough}

    def _step_think_more(self, state: Dict) -> Dict:
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
            "forneça um breve resumo atualizado das tendências de mercado relevantes em uma frase."
        )
        trends_msg = self.llm.invoke(prompt_trends)
        new_trends = trends_msg.content.strip()
        
        return {
            "iterations": new_iter,
            "thoughts": updated_thoughts,
            "market_trends": new_trends
        }

    def _step_finalize(self, state: Dict) -> Dict:
        prompt = (
            f"Usando a descrição do site:\n'{state['descriptor']}'\n"
            f"e os seguintes insights adicionais: {', '.join(state['thoughts']) if state['thoughts'] else 'Nenhum'}\n"
            f"com o resumo das tendências de mercado: '{state['market_trends']}'\n"
            "Forneça uma avaliação final do negócio em 3-5 linhas e avalie a ideia em uma escala de 1 (ruim) a 10 (excelente). "
            "Formate sua resposta como: 'Resumo Final: ...; Nota: X'"
        )
        final_msg = self.llm.invoke(prompt)
        final = final_msg.content.strip()
        import re
        match = re.search(r'Nota:\s*(\d+)', final)
        rating = int(match.group(1)) if match else 0
        return {"final_answer": final, "rating": rating}

    def _decision_router(self, state: Dict) -> str:
        if state.get("enough", False):
            return "step_finalize"
        return "step_think_more" 
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
from dotenv import load_dotenv
import os
import io
import re
from typing import List
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from bs4 import BeautifulSoup

# Load environment variables (ensure .env contains OPENAI_API_KEY)
load_dotenv()

app = FastAPI()

# ChatOpenAI LLM with the gpt-4o-mini model.
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

def fetch_website_content(url: str) -> str:
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
        f"Provide a concise, one-line descriptor summarizing the content of the website.\n\n"
        f"Content snippet:\n{snippet}"
    )
    response_msg = llm.invoke(prompt)
    descriptor = response_msg.content  # Extract text content.
    return {"descriptor": descriptor.strip()}

# Node 2: Decide if enough information is available.
def step_decision(state: State) -> dict:
    if state["iterations"] >= 3:
        return {"enough": True}
    prompt = (
        f"Based on the following website description:\n'{state['descriptor']}'\n"
        f"and the additional insights so far: {', '.join(state['thoughts']) if state['thoughts'] else 'None'}\n"
        "Do you have enough information to reliably evaluate this business idea? "
        "Answer with 'yes' or 'no'."
    )
    decision_msg = llm(prompt)
    decision_text = decision_msg.content
    enough = "yes" in decision_text.lower()
    return {"enough": enough}

# Node 3: Think more – generate an additional insight and update market trends.
def step_think_more(state: State) -> dict:
    new_iter = state["iterations"] + 1
    prompt_insight = (
        f"Website description: '{state['descriptor']}'.\n"
        f"Existing insights: {', '.join(state['thoughts']) if state['thoughts'] else 'None'}.\n"
        "What is one additional insight or factor that should be considered to evaluate this business idea? "
        "Answer in one concise sentence."
    )
    insight_msg = llm(prompt_insight)
    new_thought = insight_msg.content.strip()
    updated_thoughts = state["thoughts"] + [new_thought]
    prompt_trends = (
        f"Based on the website description '{state['descriptor']}' and the new insight '{new_thought}', "
        "provide an updated, brief summary of relevant market trends in one sentence."
    )
    trends_msg = llm(prompt_trends)
    new_trends = trends_msg.content.strip()
    return {"iterations": new_iter, "thoughts": updated_thoughts, "market_trends": new_trends}

# Node 4: Finalize the answer.
def step_finalize(state: State) -> dict:
    prompt = (
        f"Using the website description:\n'{state['descriptor']}'\n"
        f"and the following additional insights: {', '.join(state['thoughts']) if state['thoughts'] else 'None'}\n"
        f"with market trends summary: '{state['market_trends']}'\n"
        "Provide a final business evaluation in 3-5 lines and rate the business idea on a scale from 1 (poor) to 10 (excellent). "
        "Format your answer as: 'Final Summary: ...; Rating: X'"
    )
    final_msg = llm(prompt)
    final = final_msg.content.strip()
    match = re.search(r'Rating:\s*(\d+)', final)
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

# AI Agent Demo

This project demonstrates a cyclic "thinking" AI agent built using FastAPI, LangGraph, and LangChain's ChatOpenAI model (`gpt-4o-mini`). The agent fetches and sanitizes website content, generates a concise description, iteratively “thinks” to gather additional insights, and then provides a final multi-line business evaluation along with a rating.

<table style="width: 100%; table-layout: fixed;">
  <tr>
    <td style="vertical-align: top; width: 50%; padding-right: 20px;">
      <h3>🖼️ Graph Visualization</h3>
      <p>This diagram shows how the cyclic agent operates, using LangGraph to manage the flow:</p>
      <img src="visualize.png" alt="LangGraph Agent Visualization" style="width: 100%; border: 1px solid #ccc; border-radius: 8px;">
    </td>
    <td style="vertical-align: top; width: 50%; padding-left: 20px;">
      <h3>🧠 How the Agent Works</h3>
      <p><strong>1. Fetch & Sanitize Website Content</strong><br />
      The agent retrieves raw HTML and cleans it using BeautifulSoup.</p>
      <p><strong>2. Generate Descriptor</strong><br />
      The model uses ChatOpenAI to summarize the website in a single sentence.</p>

      <p><strong>3. Decision Cycle</strong><br />
      The agent loops through this process:</p>

      <ul>
        <li>Checks if it has enough information</li>
        <li>Generates additional insights if needed</li>
        <li>Updates internal thoughts and market trends</li>
        <li>Repeats (max 3 iterations)</li>
      </ul>

      <p><strong>4. Final Evaluation</strong><br />
      Once confident, the agent provides a final summary and a numeric rating (1–10).</p>
    </td>

  </tr>
</table>

## 🗂️ Project Structure

```
ai-agent-demo/
├── main.py            # Contains FastAPI endpoints and the cyclic LangGraph agent.
├── requirements.txt   # Lists project dependencies.
├── README.md          # This file.
├── .env               # Environment variables (not tracked by Git).
└── visualize.png      # Visualization of the LangGraph workflow.
```

## ⚙️ Environment Setup

The `.env` file should contain your OpenAI API key:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

Make sure not to commit this file to version control.

## 🚀 API Endpoints

### `POST /evaluate`

Trigger the agent to analyze a given website:

**Request Example:**

```json
{
  "url": "https://www.example.com"
}
```

**Response:**

```json
{
  "url": "...",
  "descriptor": "...",
  "market_trends": "...",
  "rating": 8,
  "final_answer": "Final Summary: ...; Rating: 8",
  "enough": true,
  "iterations": 2,
  "thoughts": ["...", "..."]
}
```

### `GET /visualize`

Returns a PNG of the LangGraph agent flow:

**Response:**  
Image (`visualize.png`) of the current graph layout.

## 🛠️ Installation

```bash
# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Running the App

Start the FastAPI server with Uvicorn:

```bash
uvicorn main:app --reload
```

Then open your browser at:  
👉 http://localhost:8000/docs  
to interact with the API.

## 📌 Notes

- Built with FastAPI + LangChain + LangGraph
- Powered by OpenAI’s `gpt-4o-mini`
- Uses a "cyclic agent" pattern: evaluate → think → loop → finalize
- Graph is visualized in `visualize.png` and served via `/visualize`

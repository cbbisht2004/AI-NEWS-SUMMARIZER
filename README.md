# 🤖 LangGraph Agentic AI — News Summariser & Multi-Mode Chatbot

An end-to-end agentic AI application built with **LangGraph**, **Groq LLMs**, and **Streamlit**. It ships three distinct use cases in a single web UI: a basic chatbot, a web-search-augmented chatbot, and a fully automated AI news summarisation pipeline that fetches, summarises, and persists news to Markdown files.

---

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#️-architecture)
- [Project Structure](#-project-structure)
- [Use Cases](#-use-cases)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running the App](#-running-the-app)
- [Output Files](#-output-files)
- [Tech Stack](#-tech-stack)
- [Screenshots](#-screenshots)

---

## ✨ Features

| Feature | Description |
|---|---|
| **Basic Chatbot** | Chat directly with a Groq-hosted LLM with full in-session memory |
| **Chatbot With Web** | LLM augmented with real-time Tavily web search (ReAct loop) with in-session memory |
| **AI News Summariser** | Automated pipeline: fetch → summarise → save AI news to Markdown |
| **Multiple LLMs** | Supports `llama-3.1-8b-instant`, `llama-3.3-70b-versatile`, `openai/gpt-oss-120b` via Groq |
| **In-session memory** | Conversations persist across Streamlit reruns via `InMemorySaver` checkpointer and `thread_id` |
| **Time-framed news** | Fetch news for the last day, week, or month |
| **Persistent summaries** | Summaries saved as Markdown files for later review |
| **Streamlit UI** | Clean sidebar-driven interface with API key inputs |

---

## 🏗️ Architecture

The application is structured around **LangGraph state machines**. Each use case compiles its own directed graph of nodes and edges before streaming results back to the Streamlit UI.

### AI News Pipeline Graph

```
START ──► fetch_news ──► summarize_news ──► save_result ──► END
```

1. **`fetch_news`** — Calls the Tavily Search API for "Top AI technology news India and globally" filtered by time range.
2. **`summarize_news`** — Passes raw articles to the selected Groq LLM with a structured prompt; output is sorted Markdown.
3. **`save_result`** — Writes the summary to `AINews/{daily|weekly|monthly}_summary.md`.

### Chatbot With Web Graph

```
START ──► chatbot ──► tools (Tavily) ──► chatbot ──► ... ──► END
                  └──────────────────────────────────────────┘
                         (conditional loop via tools_condition)
```

### Basic Chatbot Graph

```
START ──► chatbot ──► END
```

---

## 📁 Project Structure

```
AI NEWS SUMMARISER/
├── app.py                          # Entry point — launches Streamlit app
├── requirements.txt                # Python dependencies
├── AINews/                         # Auto-generated news summary outputs
│   ├── daily_summary.md
│   ├── weekly_summary.md
│   └── monthly_summary.md
└── src/
    └── langgraphagenticai/
        ├── main.py                 # App orchestration (UI + LLM + Graph + Display)
        ├── graph/
        │   └── graph_builder.py   # LangGraph graph construction for all use cases
        ├── nodes/
        │   ├── ai_news_node.py    # fetch_news, summarize_news, save_result nodes
        │   ├── basic_chatbot_node.py
        │   └── chatbot_with_Tool_node.py
        ├── state/
        │   └── state.py           # Shared TypedDict state with message accumulator
        ├── tools/
        │   └── search_tool.py     # Tavily search tool + LangGraph ToolNode
        ├── LLMS/
        │   └── groqllm.py         # Groq LLM initialisation wrapper
        └── ui/
            ├── uiconfigfile.ini   # UI labels, model list, and use-case options
            ├── uiconfigfile.py    # ConfigParser wrapper
            └── streamlitui/
                ├── loadui.py      # Sidebar controls, API key inputs, time-frame selector
                └── display_result.py  # Renders chat messages and Markdown news output
```

---

## 🧩 Use Cases

### 1. Basic Chatbot
A stateful chatbot with **in-session memory**. User messages are streamed through LangGraph's `graph.stream()` and the full conversation history is preserved across Streamlit reruns using an `InMemorySaver` checkpointer keyed by a per-session `thread_id`. Prior turns are replayed in the UI on each rerun.

### 2. Chatbot With Web
Extends the basic chatbot with a **Tavily web search tool** and **in-session memory**. The LLM decides when to call the tool (ReAct pattern) and loops back to synthesise a final answer. Only the clean final AI response is shown — intermediate tool call results are hidden. Context from prior turns is passed automatically via the checkpointer, so follow-up questions (e.g. "who is he?") resolve without redundant searches. Requires a **Tavily API key**.

### 3. AI News Summariser
A three-node agentic pipeline:

- Select a **time frame** (Daily / Weekly / Monthly) in the sidebar.
- Click **🔍 Fetch Latest AI News**.
- The graph fetches up to **20 news articles** from Tavily, summarises them with the LLM in structured Markdown, and saves the result.
- The rendered Markdown is displayed directly in the Streamlit UI.

Requires both a **Groq API key** and a **Tavily API key**.

---

## ✅ Prerequisites

- Python 3.10+
- A [Groq API key](https://console.groq.com/keys)
- A [Tavily API key](https://app.tavily.com/home) *(required for "Chatbot With Web" and "AI News" modes)*

---

## 🚀 Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/ai-news-summariser.git
cd ai-news-summariser

# 2. Create and activate a virtual environment
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

---

## ⚙️ Configuration

All UI labels, available models, and use-case options are controlled via [`src/langgraphagenticai/ui/uiconfigfile.ini`](src/langgraphagenticai/ui/uiconfigfile.ini):

```ini
[DEFAULT]
PAGE_TITLE       = LangGraph: Build Stateful Agentic AI graph
LLM_OPTIONS      = Groq
USECASE_OPTIONS  = Basic Chatbot, Chatbot With Web, AI News
GROQ_MODEL_OPTIONS = llama-3.1-8b-instant, llama-3.3-70b-versatile, openai/gpt-oss-120b
```

To add a new Groq model, simply append it (comma-separated) to `GROQ_MODEL_OPTIONS`.

API keys are entered **at runtime** in the Streamlit sidebar — no `.env` file is required, though you may optionally set `GROQ_API_KEY` and `TAVILY_API_KEY` as environment variables.

---

## ▶️ Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

**Sidebar workflow:**
1. Select **LLM** → `Groq`
2. Select a **Model** (e.g. `llama-3.3-70b-versatile`)
3. Enter your **GROQ API Key**
4. Select a **Use Case**
5. For *Chatbot With Web* or *AI News*, enter your **Tavily API Key**
6. For *AI News*, pick a time frame and click **🔍 Fetch Latest AI News**

---

## 📄 Output Files

After running the AI News use case, summaries are saved to the `AINews/` directory:

| File | Description |
|---|---|
| `AINews/daily_summary.md` | Top AI news from the last 24 hours |
| `AINews/weekly_summary.md` | Top AI news from the last 7 days |
| `AINews/monthly_summary.md` | Top AI news from the last 30 days |

Each file follows this Markdown structure:

```markdown
# Daily AI News Summary

### 2025-06-09
- [Article title / summary](https://source-url.com)
```

---

## 🛠️ Tech Stack

| Library | Purpose |
|---|---|
| [LangGraph](https://github.com/langchain-ai/langgraph) | Stateful agentic graph execution with `InMemorySaver` checkpointing |
| [LangChain](https://github.com/langchain-ai/langchain) | LLM abstractions, prompt templates, tool integrations |
| [Groq](https://groq.com/) | Ultra-fast LLM inference (LLaMA 3, GPT-OSS ) |
| [Tavily](https://tavily.com/) | Real-time web & news search API |
| [Streamlit](https://streamlit.io/) | Interactive web UI |

---

## 📜 License

This project is open-source. Feel free to fork, extend, and contribute.

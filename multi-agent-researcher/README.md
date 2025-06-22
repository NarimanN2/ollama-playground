# Multi-Agent AI Researcher
A multi-agent AI researcher using Qwen, LangGraph, and Streamlit to find results from the web that matches the user's query and give a summarized answer based on those results. It uses the supervisor architecture to manage multiple agents, where the main agent delegates tasks to other agents.

You can watch the video on how it was built on my [YouTube](https://youtu.be/eV-zVWClcj0).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Qwen model:

```bash
ollama pull qwen3:8b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the Streamlit app:

```bash
streamlit run multi_agent_researcher.py
```
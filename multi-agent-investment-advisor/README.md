# Multi-Agent AI Investment Advisor
A multi-agent AI investment advisor using Qwen, LangGraph, and Streamlit to provide personalized investment advice based on market data. It uses the swarm architecture to manage multiple agents, where agents can handoff tasks to each other and collaborate to provide the best investment advice.

You can watch the video on how it was built on my [YouTube](https://youtu.be/FXPYOq63eWY).

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
streamlit run multi_agent_investment_advisor.py
```
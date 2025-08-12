# ACP Agents
A local AI agent using Ollama's gpt-oss model (from OpenAI), LangChain, and Streamlit. This agent will connect to the internet using LangChain MCP adapters and Tavily, allowing it to search the web and give accurate answers to your questions.

You can watch the video on how it was built on my [YouTube](https://youtu.be/Baa-z7cum1g).

# Pre-requisites

Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the gpt-oss model:

```bash
ollama pull gpt-oss:20b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

And also create an account on [Tavily](https://tavily.com/) and get your API key. Set it as an environment variable:

```bash
export TAVILY_API_KEY=your_api_key_here
```

# Run
Run the Streamlit app:

```bash
streamlit run gpt_oss_agent_with_mcp.py
```
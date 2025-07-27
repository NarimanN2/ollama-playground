# ACP Agents
An ACP (Agent Communication Protocol) server and client setup where a LangChain agent and a CrewAI agent communicate with each other using the ACP SDK.

You can watch the video on how it was built on my [YouTube](https://youtu.be/fABcNHKVqYM).

# Pre-requisites

Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the llama model:

```bash
ollama pull llama3.2
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the servers first:

```bash
python cat_server.py
python dog_server.py
```
Then run the client:

```bash
python acp_client.py
```
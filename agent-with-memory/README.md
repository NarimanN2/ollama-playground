# Agent with Memory
A simple chatbot using Deepseek, LangGraph, and Streamlit that leverages short-term memory to recall previous interactions and provide context-aware responses.

You can watch the video on how it was built on my [YouTube](https://youtu.be/OtKMxYphw98).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:8b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the Streamlit app:

```bash
streamlit run agent_with_memory.py
```

# Bonus tip
If you want to change the short-term memory with the long-term memory, you can change the `MemorySaver` with `InMemoryStore`:

```python
from langgraph.store.memory import InMemoryStore

store = InMemoryStore()

# Example usage - Learn more about it by checking the LangGraph documentation
# store.put()
# store.get()
```

# LLM Wiki
A local LLM wiki maintainer using Ollama and LangChain that reads markdown files from your Obsidian `Clippings` folder and rebuilds a wiki inside `AI Wiki`. This is based on Andrej Karpathy’s idea. It includes:

- `llm_wiki_builder.py`: rebuilds the wiki from raw markdown sources
- `llm_wiki_maintainer.py`: a LangChain agent that answers questions about your knowledge base

It still does not implement the full incremental maintenance flow from the idea document, but the query agent follows the same pattern at a smaller scale.

You can watch the videos on my YouTube:

- [Build the wiki](https://youtu.be/l4EzuMKmeA0?si=wqP4O_w3a-99mstQ)
- [Query the wiki](https://youtu.be/4D8FjzJXJd4)

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Gemma model:

```bash
ollama pull gemma4:e4b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

Set your Obsidian vault path by updating `OBSIDIAN_DIR` in both `llm_wiki_builder.py` and `llm_wiki_maintainer.py`:

```python
OBSIDIAN_DIR = Path("PUT_YOUR_OBSIDIAN_PATH")
```

# Run
Build the wiki:

```bash
python llm_wiki_builder.py
```

Run the question-answering agent:

```bash
streamlit run llm_wiki_maintainer.py
```

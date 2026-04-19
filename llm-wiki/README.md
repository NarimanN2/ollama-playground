# LLM Wiki
A local LLM wiki maintainer using Ollama and LangChain that reads markdown files from your Obsidian `Clippings` folder and rebuilds a wiki inside `AI Wiki`. This is based on Andrej Karpathy’s idea.

This is a simplified version for educational purposes. It does not support incremental updates, a query workflow where the LLM reads the existing wiki and writes useful results back into it over time, or multimodal inputs.

You can watch the video on how it was built on my [YouTube](https://youtu.be/l4EzuMKmeA0?si=wqP4O_w3a-99mstQ).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Gemma model:

```bash
ollama pull gemma4:e4b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

Set your Obsidian vault path in `llm_wiki.py` by updating the `OBSIDIAN_DIR` placeholder:

```python
OBSIDIAN_DIR = Path("PUT_YOUR_OBSIDIAN_PATH")
```

# Run
Run the script:

```bash
python llm_wiki.py
```

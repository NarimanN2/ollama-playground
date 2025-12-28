# Local Voice Agent

Fully local voice agent using Whisper for speech-to-text, Ollama for the LLM models, and Piper for text-to-speech. Audio is captured from the mic with `streamlit-audiorec`.

## Setup

Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Llama model:

```bash
ollama pull llama3.2:latest
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

Download a Piper voice model from [Hugging Face](https://huggingface.co/rhasspy/piper-voices/tree/main) and place it under:

```
local-voice-agent/voices/
```

Run the Streamlit app:

```bash
streamlit run local_voice_agent.py
```
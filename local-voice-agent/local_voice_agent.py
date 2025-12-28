import os
import wave
import streamlit as st
import whisper
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from piper.voice import PiperVoice
from st_audiorec import st_audiorec

audios_directory = 'local-voice-agent/audios/'
voices_directory = 'local-voice-agent/voices/'

assistant_template = """
You are a helpful, conversational assistant. Keep replies short and clear.
User: {input}
Assistant:
"""

model = ChatOllama(model="llama3.2:latest")

@st.cache_resource
def load_stt():
    return whisper.load_model("base")

@st.cache_resource
def load_tts(voice_path, config_path):
    return PiperVoice.load(voice_path, config_path, use_cuda=False)

def transcribe_audio(file_path):
    stt_model = load_stt()
    result = stt_model.transcribe(file_path)
    return result["text"]

def save_recording(audio_bytes, output_path):
    with open(output_path, "wb") as audio_file:
        audio_file.write(audio_bytes)

def generate_response(text):
    prompt = ChatPromptTemplate.from_template(assistant_template)
    chain = prompt | model
    response = chain.invoke({"input": text})
    return response.content

def synthesize_audio(text, output_path):
    piper_voice_path = voices_directory + "en_US-lessac-medium.onnx"
    piper_config_path = f"{piper_voice_path}.json"

    tts_model = load_tts(piper_voice_path, piper_config_path)
    with wave.open(output_path, "wb") as wav_file:
        tts_model.synthesize_wav(text, wav_file)

st.title("Local Voice Agent")
audio_bytes = st_audiorec()
send_button = st.button("Send")

if send_button:
    if not audio_bytes:
        st.error("Record audio first!")
    else:
        with st.spinner("Transcribing audio..."):
            audio_path = audios_directory + "recording.wav"
            save_recording(audio_bytes, audio_path)
            transcription = transcribe_audio(audio_path)

        with st.spinner("Generating response..."):
            response = generate_response(transcription)

        with st.spinner("Synthesizing audio..."):
            response_path = audios_directory + "response.wav"
            synthesize_audio(response, response_path)
            st.audio(response_path)

import time

import streamlit as st
from audio_recorder_streamlit import audio_recorder

from model import TranslatorModel

from io import BytesIO


st.title("Healthcare Translation App")


audio_bytes = audio_recorder()

model = TranslatorModel()


if audio_bytes:
    # Step 1: Speech-to-Text
    transcript = model.SpeechToTranscript(audio_bytes)

    time.sleep(2)  # Pause briefly to allow for UI updates

    if transcript:
        st.write("Transcript:", transcript)

play_audio = st.button("Play Audio")

if play_audio:
    try:
        # Step 2: Text-to-Speech
        _ = model.TranscriptToSpeech(transcript)
        
        # Step 3: Play Translated Audio
        st.audio("output.mp3", format="audio/mp3")
    except:
        pass
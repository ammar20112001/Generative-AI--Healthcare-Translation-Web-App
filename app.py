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
    src_transcript = model.SpeechToTranscript(audio_bytes)

    time.sleep(2)  # Pause briefly to allow for UI updates

    if src_transcript:
        st.write("Soruce Transcript:", src_transcript)

        tgt_transcript = model.TranscriptTranslator()
        st.write("Target Transcript:", tgt_transcript)


play_audio = st.button("Play Audio")

if play_audio:
    try:
        # Step 2: Text-to-Speech
        audio_content = model.TranscriptToSpeech()
        
        # Step 3: Play Translated Audio
        st.audio(audio_content, format="audio/mp3")
    except:
        pass
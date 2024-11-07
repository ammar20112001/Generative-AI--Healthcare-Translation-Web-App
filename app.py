import threading
import time
import streamlit as st
from model import TranslatorModel

# Set up the Streamlit app
st.title("Healthcare Translation App")

# Initialize model in Streamlit session state
if 'model' not in st.session_state:
    st.session_state.model = TranslatorModel()

if 'record' not in st.session_state:
    st.session_state.record = False

# Access the model stored in session state
model = st.session_state.model
record = st.session_state.record

# Function to handle speech-to-text conversion
def speech_to_text():
    model.SpeechToTranscript()

# Function to handle continuous translation
def translate():
    model.TranscriptTranslator()

# Start real-time recording and translation
record_but = st.button("Start Real Time Recording")
stop_but = st.button("Stop Real Time Recording")
tran_but = st.button("Translate")
clear_but = st.button("Clear")

# Placeholder elements for updating the transcripts
source_placeholder = st.empty()
target_placeholder = st.empty()

if record_but:
    model.STOP_LISTENING = False
    record = True

    # Start speech-to-text and translation in background threads
    t1 = threading.Thread(target=speech_to_text)
    t2 = threading.Thread(target=translate)
    t1.start()
    t2.start()

    # Update the transcripts in the main loop
    while record:
        source_text = " ".join(model.src_transcript)
        target_text = model.tgt_transcript

        source_placeholder.write(f"Source transcript: {source_text}")
        target_placeholder.write(f"Target transcript: {target_text}")
        
        time.sleep(1)  # Update every second

if stop_but:
    model.STOP_LISTENING = True
    record = False

if tran_but:
    model.STOP_LISTENING = False
    translate()
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")
    model.STOP_LISTENING = True

if clear_but:
    model.src_transcript = []
    model.tgt_transcript = ""
    source_placeholder.write("Source transcript: ")
    target_placeholder.write("Target transcript: ")

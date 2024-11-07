import threading
import time
import streamlit as st
from model import TranslatorModel

# Set up the Streamlit app
st.title("Healthcare Translation App")

# Start real-time recording and translation
record_but = st.button("Start Real Time Recording")
stop_but = st.button("Stop Real Time Recording")
tran_but = st.button("Change Translate")
clear_but = st.button("Clear")

# Initialize model in Streamlit session state
if 'model' not in st.session_state:
    st.session_state.model = TranslatorModel()

if 'record' not in st.session_state:
    st.session_state.record = False

if 'source_placeholder' not in st.session_state:
    st.session_state.source_placeholder = st.empty()

if 'target_placeholder' not in st.session_state:
    st.session_state.target_placeholder = st.empty()

# Access the model stored in session state
model = st.session_state.model
record = st.session_state.record
source_placeholder = st.session_state.source_placeholder
target_placeholder = st.session_state.target_placeholder

# Function to handle speech-to-text conversion
def speech_to_text():
    model.SpeechToTranscript()

# Function to handle continuous translation
def translate(run_once=False):
    if not run_once:
        model.TranscriptTranslator()
    else:
        model.TranscriptTranslator(run_once=True)

# Placeholder elements for updating the transcripts
source_placeholder.write(f"Source transcript: {" ".join(model.src_transcript)}")
target_placeholder.write(f"Target transcript: {model.tgt_transcript}")

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
    record = True

if tran_but:
    model.STOP_LISTENING = False
    translate(run_once=True)
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")
    model.STOP_LISTENING = True

if clear_but:
    model.src_transcript = []
    model.tgt_transcript = ""
    source_placeholder.write("Source transcript: ")
    target_placeholder.write("Target transcript: ")

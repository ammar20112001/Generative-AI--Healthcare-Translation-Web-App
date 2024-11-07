import threading
import time
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from model import TranslatorModel
from io import BytesIO

# Set up the Streamlit app
st.title("Healthcare Translation App")

# Initialize audio recording (if you want to record audio)
audio_bytes = None
# audio_bytes = audio_recorder()

# Initialize model in Streamlit session state
if 'model' not in st.session_state:
    st.session_state.model = TranslatorModel()

# Access the model stored in session state
model = st.session_state.model

# Function to handle speech-to-text conversion
def speech_to_text():
    model.SpeechToTranscript()

# Function to handle continuous translation
def translate():
    while True:
        # Get the latest transcript and store it in session state
        translation = model.TranscriptTranslator()
        print(translation)
        st.write(translation)
        st.session_state.translated_text = translation
        time.sleep(1)  # Check every 1 second for new transcript to translate

# Start real-time recording and translation
but = st.button("Start Real Time Recording")

if but:
    st.write("Both threads are running concurrently.")
    st.write("Source transcript", model.src_transcript)
    st.write("Target transcript", model.tgt_transcript)
    # Start the speech-to-text thread
    thread1 = threading.Thread(target=speech_to_text)
    thread1.start()

    # Start the translation thread, which continuously checks for new transcripts
    thread2 = threading.Thread(target=translate)
    thread2.daemon = True  # This will allow thread2 to exit when the main program exits
    thread2.start()

    # Wait for thread1 (speech-to-text) to finish
    thread1.join()

    # Use st.empty() to display the translation in real-time
    translation_placeholder = st.empty()

    # Continuously update the translation from session_state
    while thread1.is_alive() or thread2.is_alive():
        if 'translated_text' in st.session_state:
            # Update the UI with the latest translation from session_state
            translation_placeholder.write(f"\n\nTRANSLATION\n\n{st.session_state.translated_text}")
        time.sleep(1)

    

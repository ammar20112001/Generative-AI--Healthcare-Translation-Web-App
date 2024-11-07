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
    # Get the latest transcript and store it in session state
    translation = model.TranscriptTranslator()

def update():
    while not model.STOP_LISTENING:
        st.write("Source transcript:", " ".join(model.src_transcript))
        st.write("Target transcript:", model.tgt_transcript)
        time.sleep(1)


# Start real-time recording and translation
record_but = False
stop_but = False
record_but = st.button("Start Real Time Recording")
stop_but = st.button("Stop Real Time Recording")
tran_but = st.button("Translate")
update_but = st.button("Update")
clear_but = st.button("Clear")

#while(True):
#    if record_but:
        
#        st.write("Translating/Transcripting...")
#        st.write("Source transcript:", " ".join(model.src_transcript))
#        st.write("Target transcript:", model.tgt_transcript)

        # Start the speech-to-text thread
#        thread1 = threading.Thread(target=speech_to_text)
#        thread1.start()

        # Start the translation thread, which continuously checks for new transcripts
#        thread2 = threading.Thread(target=translate)
        #thread2.daemon = True  # This will allow thread2 to exit when the main program exits
#        thread2.start()

        # Wait for thread1 (speech-to-text) to finish
#        thread1.join()
#        thread2.join()

        # Use st.empty() to display the translation in real-time
#        translation_placeholder = st.empty()

        # Continuously update the translation from session_state
        #while thread1.is_alive() or thread2.is_alive():
        #    if 'translated_text' in st.session_state:
        #        # Update the UI with the latest translation from session_state
        #        translation_placeholder.write(f"\n\nTRANSLATION\n\n{st.session_state.translated_text}")
        #    time.sleep(1)

        
#    if stop_but:
#        model.STOP_LISTENING = True
#        break


if len(model.src_transcript)>0 or model.tgt_transcript or update_but or clear_but:
    st.write(f"Source transcript: {" ".join(model.src_transcript)}")
    st.write(f"Target transcript: {model.tgt_transcript}")

if record_but:
    model.STOP_LISTENING = False
    record = True

    t1 = threading.Thread(target=speech_to_text)
    t2 = threading.Thread(target=translate)
    #t3 = threading.Thread(target=update)

    t1.start()
    t2.start()
    #t3.start()

    t1.join()
    t2.join()
    #t3.join()

    print("DONE!")
        
if stop_but:
    model.STOP_LISTENING = True
    record = False

if tran_but:
    model.STOP_LISTENING = False
    translate()
    model.STOP_LISTENING = True

if clear_but:
    model.src_transcript = []
    model.tgt_transcript = ""
        


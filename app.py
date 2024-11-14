import threading
import time
import streamlit as st
from model import TranslatorModel
from browser_app import BrowserMicrophone
from tempfile import NamedTemporaryFile


from audio_recorder_streamlit import audio_recorder

is_brw_model = False

# Set up the Streamlit app title
st.title("Healthcare Translation App")

# Create a two-column layout: left side for controls, right side for transcripts and other outputs
col1, col2 = st.columns([1, 2])  # Left side is smaller (1), right side is larger (2)
from languages import languages


# Create a list of language names for selection
language_names = list(languages.keys())

# Create a list of language names for selection
language_names = list(languages.keys())

# Display the selectboxes for source and target language selection
st.sidebar.header("Language Selection")

# Source language selection
source_language = st.sidebar.selectbox("Select Source Language", language_names)

# Target language selection
target_language = st.sidebar.selectbox("Select Target Language", language_names)

# Display the selected languages
st.write(f"Source Language: {source_language} ({languages[source_language]})")
st.write(f"Target Language: {target_language} ({languages[target_language]})")


# Buttons and file upload on the left side (column 1)
with col1:
    brw_record_but = audio_recorder("Record from browser")
    record_but = st.button("Start Real Time Recording")
    stop_but = st.button("Stop Real Time Recording")
    tran_but = st.button("Change Translate")
    clear_but = st.button("Clear")
    play_audio = st.button("Play Audio")
    audio = st.file_uploader("Upload an audio file", type=["mp3"])

# Initialize model in Streamlit session state
if 'model' not in st.session_state:
    st.session_state.model = TranslatorModel(src_lang=languages[source_language], 
                                             tgt_lang=languages[target_language],
                                             src_lang_name=source_language, 
                                             tgt_lang_name=target_language)

if 'brw_model' not in st.session_state:
    st.session_state.brw_model = BrowserMicrophone(src_lang=languages[source_language])

if 'record' not in st.session_state:
    st.session_state.record = False

with col2:
    if 'source_placeholder' not in st.session_state:
        st.session_state.source_placeholder = st.empty()

    if 'target_placeholder' not in st.session_state:
        st.session_state.target_placeholder = st.empty()

# Check if the source or target language has changed
if 'audio_bytes' not in st.session_state:
    st.session_state.audio_bytes = bytearray()

if 'prev_source_language' not in st.session_state:
    st.session_state.prev_source_language = target_language

if 'prev_target_language' not in st.session_state:
    st.session_state.prev_target_language = target_language

# Detect language change
if source_language != st.session_state.prev_source_language or target_language != st.session_state.prev_target_language:
    # Reset the model instance
    st.session_state.model = TranslatorModel(src_lang=languages[source_language], 
                                             tgt_lang=languages[target_language],
                                             src_lang_name=source_language, 
                                             tgt_lang_name=target_language)
    
    st.session_state.brw_model = BrowserMicrophone(src_lang=languages[source_language])
    
    # Update previous language states
    st.session_state.prev_source_language = source_language
    st.session_state.prev_target_language = target_language

# Access the model stored in session state
model = st.session_state.model
brw_model = st.session_state.brw_model
record = st.session_state.record
source_placeholder = st.session_state.source_placeholder
target_placeholder = st.session_state.target_placeholder
audio_bytes = st.session_state.audio_bytes

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
with col2:
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")

# Handling buttons' actions
if record_but:
    model.STOP_LISTENING = False

    # Start speech-to-text and translation in background threads
    t1 = threading.Thread(target=speech_to_text)

    t2 = threading.Thread(target=translate)
    t1.start()
    t2.start()

    # Update the transcripts in the main loop
    while record:
        source_text = " ".join(model.src_transcript)
        target_text = model.tgt_transcript
        
        with col2:
            # Display updated transcripts
            source_placeholder.write(f"Source transcript: {source_text}")
            target_placeholder.write(f"Target transcript: {target_text}")
        
        time.sleep(1)  # Update every second


# Handling buttons' actions
if brw_record_but:
    brw_model.STOP_LISTENING = False

    def fill_buff():
        brw_model._buff.put(brw_record_but)
        transcript = brw_model.convert_browser(brw_record_but)
        #audio_bytes = brw_model._buff.get()
        #st.audio(audio_bytes, format="audio/mp3")
        if [transcript] != [None]:
            print("BEFOREEE:",model.src_transcript)
            model.src_transcript.append(transcript)
            print("AFTERRR:",model.src_transcript)
        model.TranscriptTranslator(run_once=True)

        source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
        target_placeholder.write(f"Target transcript: {model.tgt_transcript}")

    fill_buff()

if stop_but:
    model.STOP_LISTENING = True
    record = False  # Stopping the recording

if tran_but:
    model.STOP_LISTENING = False
    translate(run_once=True)
    source_placeholder.write(f"Source transcript: {' '.join(model.src_transcript)}")
    target_placeholder.write(f"Target transcript: {model.tgt_transcript}")
    model.STOP_LISTENING = True

if clear_but:
    model.src_transcript = [""]
    model.tgt_transcript = ""
    source_placeholder.write("Source transcript: ")
    target_placeholder.write("Target transcript: ")

if play_audio:
    try:
        # Step 2: Text-to-Speech
        audio_content = model.TranscriptToSpeech()
        
        # Step 3: Play Translated Audio
        st.audio(audio_content, format="audio/mp3")
    except:
        pass

# Handling audio file upload
if audio is not None:
    # Save the uploaded file to a temporary file on disk
    with NamedTemporaryFile(suffix=".mp3", delete=False) as temp:
        temp.write(audio.getvalue())  # Write the audio content to the temporary file
        temp.seek(0)
        
        # Get the path of the temporary file
        temp_file_path = temp.name
        
        # Pass the file path to the model function (assumes `SpeechToTranscript` expects a file path)
        result = model.SpeechToTranscript(audio_sm=temp_file_path)

    # Display the transcription result on the right side
    with col2:
        st.write(f"Source sentence: {" ".join(model.src_transcript)}")
        st.write(f"Target sentence: {model.TranscriptTranslator(run_once=True)}")

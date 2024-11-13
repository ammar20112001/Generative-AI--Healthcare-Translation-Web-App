import threading
import asyncio
import queue
# app.py
import streamlit as st
import asyncio
import websockets
import base64
from io import BytesIO
from pydub import AudioSegment
from google.cloud import speech
from google.oauth2 import service_account
import json
import os

# Google Speech-to-Text setup
gcp_key = json.loads(os.getenv("GCP_KEY_MEDICAL_TRANSLATOR"))
credentials = service_account.Credentials.from_service_account_info(gcp_key)
client = speech.SpeechClient(credentials=credentials)

st.title("Real-Time Speech Transcription and Translation")

# JavaScript code to start and stop recording, and send audio data via WebSocket
audio_recorder_js = """
<script>
    let mediaRecorder;
    let audioChunks = [];
    const websocket = new WebSocket("ws://localhost:8660");

    websocket.onopen = () => {
        console.log("WebSocket connection established");
    };

    websocket.onerror = error => {
        console.error("WebSocket error:", error);
    };

    websocket.onmessage = event => {
        const transcript = event.data;
        console.log("Transcript:", transcript);
        document.getElementById("transcript-display").innerText = "Transcript: " + transcript;
    };

    function startRecording() {
        navigator.mediaDevices.getUserMedia({ audio: true })
        .then(stream => {
            mediaRecorder = new MediaRecorder(stream);
            mediaRecorder.ondataavailable = event => {
                audioChunks.push(event.data);
                console.log("Audio Chunk:", event.data);
            };
            mediaRecorder.onstop = () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                const reader = new FileReader();
                reader.onloadend = () => {
                    const base64Audio = reader.result.split(',')[1];
                    websocket.send(base64Audio); // Send audio data to server
                };
                reader.readAsDataURL(audioBlob);
                audioChunks = [];
            };
            mediaRecorder.start();
            console.log("Recording started");
        });
    }

    function stopRecording() {
        mediaRecorder.stop();
        console.log("Recording stopped");
    }
</script>

<button onclick="startRecording()">Start Recording</button>
<button onclick="stopRecording()">Stop Recording</button>
<div id="transcript-display"></div>
"""

st.components.v1.html(audio_recorder_js)

# WebSocket server to handle real-time transcription
async def handle_audio(websocket, path='None'):
    """Handle incoming audio, send to Google Speech API, and return transcriptions."""
    
    # Google Speech-to-Text configuration
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(
        config=config, interim_results=True
    )

    audio_input = queue.Queue()

    def audio_stream_generator():
        """Generate audio data chunks to send to Google Speech API."""
        while True:
            chunk = audio_input.get()
            if chunk is None:
                break
            yield speech.StreamingRecognizeRequest(audio_content=chunk)

    def start_google_speech():
        """Start the Google Speech API streaming recognizer in a separate thread."""
        try:
            responses = client.streaming_recognize(streaming_config, audio_stream_generator())
            # Process the responses
            for response in responses:
                if response.results:
                    for result in response.results:
                        transcript = result.alternatives[0].transcript
                        print(f"Transcript: {transcript}")
                        asyncio.run(websocket.send(transcript))  # Send transcript back to the client
        except Exception as e:
            print(f"Error getting response: {e}")

    # Start Google Speech API in a separate thread
    google_thread = threading.Thread(target=start_google_speech)
    google_thread.start()

    try:
        while True:
            audio_data = await websocket.recv()
            audio_input_data = base64.b64decode(audio_data)
            audio = AudioSegment.from_file(BytesIO(audio_input_data))
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)

            # Export audio to WAV format for API
            mono_audio_data = BytesIO()
            audio.export(mono_audio_data, format="wav")
            audio_input.put(mono_audio_data.getvalue())

    except Exception as e:
        print(f"Error processing audio: {e}")
    finally:
        audio_input.put(None)  # Stop the audio stream

# Start WebSocket server
async def main():
    async with websockets.serve(handle_audio, "localhost", 8660):
        await asyncio.Future()  # Run server forever

asyncio.run(main())
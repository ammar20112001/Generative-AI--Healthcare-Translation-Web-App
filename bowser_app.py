import sys
import re

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

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class BrowserMicrophone():

    def __init__(self: object, rate: int = RATE, chunk: int = CHUNK) -> None:

        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        #self.closed = True

        self.src_transcript = [""]

        self.STOP_LISTENING = False


    def ListenFromBrowser(self, audio_input):
        language_code = "en-US"  # a BCP-47 language tag

        client = speech.SpeechClient(credentials=credentials)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        while self.STOP_LISTENING:
            audio_generator = self.generator()

            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            self.listen_print_loop(responses)


    def _fill_buffer(
            self: object,
            in_data: object,
            frame_count: int,
            time_info: object,
            status_flags: object,
        ) -> None:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data) # Continuously collect data from the audio stream, into the buffer


    def generator(self):
        """Generate audio data chunks to send to Google Speech API."""

        chunk = self._buff.get()
        if chunk is None:
            return
        data = [chunk]
        
        while True:
            try:
                chunk = self._buff.get()
                if chunk is None:
                    break
                data.append(chunk)
            except queue.Empty:
                break
        
        yield b"".join(data)


    def listen_print_loop(self, responses: object) -> str:
        """Iterates through server responses and prints them.

        The responses passed is a generator that will block until a response
        is provided by the server.

        Each response may contain multiple results, and each result may contain
        multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
        print only the transcription for the top alternative of the top result.

        In this case, responses are provided for interim results as well. If the
        response is an interim one, print a line feed at the end of it, to allow
        the next result to overwrite it, until the response is a final one. For the
        final one, print a newline to preserve the finalized transcription.

        Args:
            responses: List of server responses

        Returns:
            The transcribed text.
        """
        num_chars_printed = 0
        for response in responses:
            if not response.results:
                continue

            # The `results` list is consecutive. For streaming, we only care about
            # the first result being considered, since once it's `is_final`, it
            # moves on to considering the next utterance.
            result = response.results[0]
            if not result.alternatives:
                continue

            # Display the transcription of the top alternative.
            transcript = result.alternatives[0].transcript

            # Display interim results, but with a carriage return at the end of the
            # line, so subsequent lines will overwrite them.
            #
            # If the previous result was longer than this one, we need to print
            # some extra spaces to overwrite the previous result
            overwrite_chars = " " * (num_chars_printed - len(transcript))

            if self.STOP_LISTENING:
                print(transcript + overwrite_chars)
                print("Exiting..")
                break

            if not result.is_final:
                sys.stdout.write(transcript + overwrite_chars + "\r")
                self.src_transcript[-1] = transcript + overwrite_chars
                #print("\nInside: ",self.src_transcript)
                sys.stdout.flush()

                num_chars_printed = len(transcript)

            else:
                #print(transcript + overwrite_chars)
                self.src_transcript.append("")
                #print("\nOutside: ",self.src_transcript)

                # Exit recognition if any of the transcribed phrases could be
                # one of our keywords.
                if re.search(r"\b(exit|quit)\b", transcript, re.I):
                    print("Exiting..")
                    break

                num_chars_printed = 0

            print("Coming out of listening loop")
            return transcript

        return transcript

   

# Start WebSocket server
async def main():
    async with websockets.serve(handle_audio, "localhost", 8660):
        await asyncio.Future()  # Run server forever

asyncio.run(main())










"""def start_google_speech():
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
        audio_input.put(None)  # Stop the audio stream"""
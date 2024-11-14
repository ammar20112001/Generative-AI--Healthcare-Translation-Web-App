import os

import json

import queue
import re
import sys

from google.cloud import speech
from google.oauth2 import service_account

import pyaudio

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

gcp_key = json.loads(os.getenv("GCP_KEY_MEDICAL_TRANSLATOR"))
credentials = service_account.Credentials.from_service_account_info(gcp_key)

client = speech.SpeechClient(credentials=credentials)

# server.py
import asyncio
import websockets
import base64

from io import BytesIO
from pydub import AudioSegment

class RealTimeTranscriber:
    def __init__(self, src_lang='en-US'):
        self.src_lang = src_lang
        self.client = speech.SpeechClient()

    async def handle_audio(self, websocket, path):
        # Prepare streaming configuration for Google Speech-to-Text
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
            language_code=self.src_lang,
        )
        streaming_config = speech.StreamingRecognitionConfig(config=config, interim_results=True)
        
        # Create a generator to yield audio chunks for the API
        async def audio_stream_generator():
            async for message in websocket:
                audio_input = base64.b64decode(message)
                # Convert to mono and 16kHz
                audio = AudioSegment.from_file(BytesIO(audio_input))
                audio = audio.set_channels(1)
                audio = audio.set_frame_rate(16000)
                
                # Export the processed audio to bytes
                mono_audio_data = BytesIO()
                audio.export(mono_audio_data, format="wav")
                yield speech.StreamingRecognizeRequest(audio_content=mono_audio_data.getvalue())

        # Send audio chunks to the streaming API
        responses = self.client.streaming_recognize(config=streaming_config, requests=audio_stream_generator())
        
        # Process responses from Google API and send transcripts to the client
        async for response in responses:
            for result in response.results:
                transcript = result.alternatives[0].transcript
                print(f"Transcript: {transcript}")
                await websocket.send(transcript)  # Send transcript back to the client

async def main():
    transcriber = RealTimeTranscriber()
    async with websockets.serve(transcriber.handle_audio, "localhost", 8502):
        await asyncio.Future()  # Run server forever

asyncio.run(main())
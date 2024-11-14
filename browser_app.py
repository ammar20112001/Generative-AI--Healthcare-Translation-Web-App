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


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


class BrowserMicrophone():

    def __init__(self: object, src_lang, rate: int = RATE, chunk: int = CHUNK) -> None:

        self._rate = rate
        self._chunk = chunk

        self._buff = queue.Queue()
        #self.closed = True

        self.src_transcript = [""]

        self.STOP_LISTENING = False

        self.src_lang = src_lang


    def ListenFromBrowser(self):
        language_code = "en-US"  # a BCP-47 language tag

        client = speech.SpeechClient(credentials=credentials)
        print("POINT1")
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code="en-US",
        )
        print("POINT2")
        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )
        print("POINT3")
        while not self.STOP_LISTENING:
            print("POINT3.5")
            audio_generator = self.generator()
            print("POINT4")
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )
            print("POINT5")
            responses = client.streaming_recognize(streaming_config, requests)
            print("POINT5")
            # Now, put the transcription responses to use.
            self.listen_print_loop(responses)


    def convert_browser(self, audio_input):
        # Convert audio to mono using pydub
        audio = AudioSegment.from_file(BytesIO(audio_input))
        audio = audio.set_channels(1)  # Convert to mono
        audio = audio.set_frame_rate(16000)  # Optionally set to 16000 Hz

        # Export the processed audio to bytes
        mono_audio_data = BytesIO()
        audio.export(mono_audio_data, format="wav")
        mono_audio_data = mono_audio_data.getvalue()

        # Use 'content' to pass raw audio data directly to the Google API
        audio = speech.RecognitionAudio(content=mono_audio_data)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            #sample_rate_hertz=16000,
            language_code=self.src_lang,
        )

        # Detects speech in the audio file
        response = client.recognize(config=config, audio=audio)

        for result in response.results:
            print(str(result.alternatives[0].transcript))
            return str(result.alternatives[0].transcript)


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
        print("ENTERED BUFFER!!")    
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


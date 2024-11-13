import os

import json

import queue
import re
import sys

from google.oauth2 import service_account

from google.cloud import speech, texttospeech
from openai import OpenAI

from pydub import AudioSegment
import pyaudio

from io import BytesIO


# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms


api_key = os.getenv("OPENAI_API_KEY_MEDICAL_TRANSLATOR")
gcp_key = json.loads(os.getenv("GCP_KEY_MEDICAL_TRANSLATOR"))
credentials = service_account.Credentials.from_service_account_info(gcp_key)


class TranslatorModel():

    def __init__(self, 
                 src_lang: str, 
                 tgt_lang: str, 
                 src_lang_name: str, 
                 tgt_lang_name: str, 
                 config=None):
        
        self.client = speech.SpeechClient(credentials=credentials)

        self.speech_to_transcript = SpeechToTranscript(src_lang=src_lang)
        self.transcript_translator = TranscriptTranslator(src_lang_name=src_lang_name, tgt_lang_name=tgt_lang_name)
        self.transcript_cleaner = TranscriptCleaner(src_lang_name=src_lang_name)
        self.medical_terms_cleaner = MedicalTermsCleaner(src_lang_name=src_lang_name)
        self.transcript_to_speech = TranscriptToSpeech(tgt_lang=tgt_lang)
        self.MicrophoneStream = MicrophoneStream()
        
        self.src_transcript = [""]
        self.tgt_transcript = ""

        self.STOP_LISTENING = False

    def SpeechToTranscript(self, audio_input=None, audio_sm=None):
        
        if audio_sm == None:
            if audio_input:
                self.src_transcript = self.speech_to_transcript.convert_(audio_input)
                return self.src_transcript
            
            else:
                transcript = self.speech_to_transcript.convert(self.listen_print_loop)
                return transcript
        
        else:
            transcript = self.speech_to_transcript.convert_audio_sm(audio_file=audio_sm)
            self.src_transcript = [" ".join([res.alternatives[0].transcript for res in transcript.results]), "", "", ""]
            self.TranscriptCleaner() # Cleaning transcription from spelling and grammatical mistakes
            self.MedicalTermsCleaner() # Fixing medical terminologies
            return transcript


    def TranscriptCleaner(self, run_once=False):
        if len(" ".join(self.src_transcript))>15:
            #print("\nself.src_transcript",self.src_transcript)
            try:
                src_text = " ".join(self.src_transcript)
            except:
                return
            response = self.transcript_cleaner.convert(src_text)
            #print("Transcript: ",self.src_transcript)
            self.src_transcript = [response, ""]
            #print("self.src_transcript",self.src_transcript, "\n")

    
    def MedicalTermsCleaner(self, run_once=False):
        if len(" ".join(self.src_transcript))>15:
            #print("\nself.src_transcript",self.src_transcript)
            try:
                src_text = " ".join(self.src_transcript)
            except:
                return
            response = self.medical_terms_cleaner.convert(src_text)
            #print("Transcript: ",self.src_transcript)
            self.src_transcript = [response, ""]
            #print("self.src_transcript",self.src_transcript, "\n")


    def TranscriptTranslator(self, run_once=False):
        if not run_once:
            while not self.STOP_LISTENING:
                self.TranscriptCleaner() # Cleaning transcription from spelling and grammatical mistakes
                self.MedicalTermsCleaner() # Fixing medical terminologies

                src_text = " ".join(self.src_transcript)
                self.tgt_transcript = self.transcript_translator.convert(src_text)
            return self.tgt_transcript
        else:
            try:
                src_text = " ".join(self.src_transcript)
            except:
                src_text = [self.src_transcript, "", "", ""]
            self.tgt_transcript = self.transcript_translator.convert(src_text)
            return self.tgt_transcript


    def TranscriptToSpeech(self, text_input=None):
        if text_input:
            return self.transcript_to_speech.convert(text_input)
        else:
            return self.transcript_to_speech.convert(self.tgt_transcript)
        
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


            #last_window = transcript.split(" ")[-1]
            #self.src_transcript.append(last_window)
           

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

        return transcript
        

class MicrophoneStream:
    """Opens a recording stream as a generator yielding the audio chunks."""

    def __init__(self: object, rate: int = RATE, chunk: int = CHUNK) -> None:
        """The audio -- and generator -- is guaranteed to be on the main thread."""
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self: object) -> object:
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1,
            rate=self._rate,
            input=True,
            frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(
        self: object,
        type: object,
        value: object,
        traceback: object,
    ) -> None:
        """Closes the stream, regardless of whether the connection was lost or not."""
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(
        self: object,
        in_data: object,
        frame_count: int,
        time_info: object,
        status_flags: object,
    ) -> object:
        """Continuously collect data from the audio stream, into the buffer.

        Args:
            in_data: The audio data as a bytes object
            frame_count: The number of frames captured
            time_info: The time information
            status_flags: The status flags

        Returns:
            The audio data as a bytes object
        """
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self: object) -> object:
        """Generates audio chunks from the stream of audio data in chunks.

        Args:
            self: The MicrophoneStream object

        Returns:
            A generator that outputs audio chunks.
        """
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b"".join(data)



class SpeechToTranscript():

    def __init__(self, src_lang: str):
        # Instantiates a client
        self.client = speech.SpeechClient(credentials=credentials)
        self.src_lang = src_lang

    def convert(self, listen_print_loop) -> None:
        """Transcribe speech from audio file."""
        # See http://g.co/cloud/speech/docs/languages
        # for a list of supported languages.
        language_code = self.src_lang  # a BCP-47 language tag

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code,
        )

        streaming_config = speech.StreamingRecognitionConfig(
            config=config, interim_results=True
        )

        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (
                speech.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator
            )

            responses = self.client.streaming_recognize(streaming_config, requests)

            # Now, put the transcription responses to use.
            transcript = listen_print_loop(responses=responses)

            #self.src_transcript = [transcript]

            return transcript

        
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
        response = self.client.recognize(config=config, audio=audio)

        for result in response.results:
            return str(result.alternatives[0].transcript)
        
    
    def convert_audio_sm(self, audio_file: str) -> speech.RecognizeResponse:
        """Transcribe the given audio file.
        Args:
            audio_file (str): Path to the local audio file to be transcribed.
                Example: "resources/audio.wav"
        Returns:
            cloud_speech.RecognizeResponse: The response containing the transcription results
        """
        client = speech.SpeechClient(credentials=credentials)

        with open(audio_file, "rb") as f:
            audio_content = f.read()

        audio = speech.RecognitionAudio(content=audio_content)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.MP3,
            sample_rate_hertz=16000,
            language_code=self.src_lang,
        )

        response = client.recognize(config=config, audio=audio)

        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            print(f"Transcript: {result.alternatives[0].transcript}")

        return response


class TranscriptCleaner():

    def __init__(self, src_lang_name: str):
        self.client = OpenAI(api_key=api_key)
        self.src_lang_name = src_lang_name

    def convert(self, src_text):

        if len(src_text)>3:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""You are an expert on {self.src_lang_name} language. Your job is to clean the 
                        audio transcriptions by reading the transcriptions, fixing spelling mistakes, and punctuating 
                        the sentence. You cannot change words, or sentences, or sentence structures. Write the 
                        corrected transcription within the double quotation marks \"\". if there's nothing to change,
                        just re-write the entire sentence as it is inside double quotation marks. And do not write 
                        anything else within your response.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""Clean the following {self.src_lang_name} sentence and please make sure that 
                        you write your response in \"\" double quotation marks only and not write anythign else in 
                        your response, other than the cleaned sentence: 
                        
                        {src_text}"""
                    }
                ]
            )

            try:
                response = completion.choices[0].message.content.split("\"")[1].split("\"")[0]
            except:
                print("PARSING ERROR WHILE CLEANING")
                return src_text

            if len(response) < len(src_text)//2:
                #print("\nCLEANING (short len):")
                #print("Before:",src_text)
                #print("After:",src_text,"\n")
                return src_text

            #print("\nCLEANING: (try)")
            #print("Before:",src_text)
            #print("After:",response,"\n")
            return response

        else:
            #print("\nCLEANING (else):")
            #print("Before:",src_text)
            #print("After:",src_text,"\n")
            return src_text
        

class MedicalTermsCleaner():

    def __init__(self, src_lang_name: str):
        self.client = OpenAI(api_key=api_key)
        self.src_lang_name = src_lang_name

    def convert(self, src_text):

        if len(src_text)>3:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": f"""
                        You are a medical expert. Your job is to review audio transcripts that have 
                        medical terminologies written within the sentence, and fix if there's any spelling mistke in 
                        the terminology or many times the medical terminologies are transcripted with wrong words. 
                        If you detect any of the 2 possible cases, rewrite the entire sentence with fixed medical 
                        terminologies inside double quotation marks "", and do not write anything else within your 
                        response. If there is nothing to fix, just re-write the entire sentence inside "" double quotation marks.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""
                        Check the following {self.src_lang_name} sentence and fix if there's any medical terminology
                        that's written incorrectly. Rewrite the entire sentence with fixed medical terminologies inside 
                        double quotation marks "", and do not write anything else within your response. If there is
                        nothing to fix, just re-write the entire sentence inside "" double quotation marks.
                        
                        {src_text}
                        """
                    }
                ]
            )
            
            try:
                response = completion.choices[0].message.content.split("\"")[1].split("\"")[0]
            except:
                print("PARSING ERROR WHILE CLEANING")
                return src_text

            if len(response) < len(src_text)//2:
                print("\nMEDICAL (short len):")
                print("Before:",src_text)
                print("After:",src_text,"\n")
                return src_text

            print("\nMEDICAL: (try)")
            print("Before:",src_text)
            print("After:",response,"\n")
            return response

        else:
            print("\nMEDICAL (else):")
            print("Before:",src_text)
            print("After:",src_text,"\n")
            return src_text

class TranscriptTranslator():

    def __init__(self, src_lang_name: str, tgt_lang_name: str):
        self.client = OpenAI(api_key=api_key)
        self.src_lang_name = src_lang_name
        self.tgt_lang_name = tgt_lang_name

    def convert(self, src_text):

        if len(src_text)>3:
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a Translator, who knows all langauges. All you do is write translation 
                        from source language to target language within quotation marks "". You don't say anything else, 
                        only and only translation in the target langauge.
                        """
                    },
                    {
                        "role": "user",
                        "content": f"""Translate the following sentence from {self.src_lang_name} to {self.tgt_lang_name}: 
                        
                        {src_text}
                        """
                    }
                ]
            )
            try:
                return completion.choices[0].message.content.split("\"")[1].split("\"")[0]
            except:
                return completion.choices[0].message.content
        else:
            return ""


class TranscriptToSpeech():

    def __init__(self, tgt_lang: str):
        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient(credentials=credentials)
        self.tgt_lang = tgt_lang

    def convert(self, text_input):
        text = text_input

        input_text = texttospeech.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams(
            language_code=self.tgt_lang,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        response = self.client.synthesize_speech(
            request={"input": input_text, "voice": voice, "audio_config": audio_config}
        )

        # The response's audio_content is binary.
        with open("output.mp3", "wb") as out:
            out.write(response.audio_content)
            print('Audio content written to file "output.mp3"')

        return BytesIO(response.audio_content)


if __name__ == "__main__":
    model = TranslatorModel()

    model.SpeechToTranscript()
    translation = model.TranscriptTranslator()
    print(translation)
    model.TranscriptToSpeech()

from google.cloud import speech, texttospeech

from pydub import AudioSegment
from io import BytesIO


class TranslatorModel():

    def __init__(self, config=None):
        self.speech_to_transcript = SpeechToTranscript()
        self.transcript_translator = TranscriptTranslator
        self.transcript_to_speech = TranscriptToSpeech()
        self.transcript = None

    def SpeechToTranscript(self, audio_input):
        self.transcript = self.speech_to_transcript.convert(audio_input)
        return self.transcript

    def TranscriptTranslator(self):
        pass

    def TranscriptToSpeech(self, text_input=None):
        if text_input:
            self.transcript_to_speech.convert(text_input)
        else:
            self.transcript_to_speech.convert(self.transcript)



class SpeechToTranscript():

    def __init__(self):
        # Instantiates a client
        self.client = speech.SpeechClient.from_service_account_file('medicaltranslator-99340673597e.json')

        
    def convert(self, audio_input):
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
            language_code="en-US",
        )

        # Detects speech in the audio file
        response = self.client.recognize(config=config, audio=audio)

        for result in response.results:
            return str(result.alternatives[0].transcript)



class TranscriptTranslator():

    def __init__(self):
        pass


class TranscriptToSpeech():

    def __init__(self):
        # Instantiates a client
        self.client = texttospeech.TextToSpeechClient.from_service_account_file('medicaltranslator-99340673597e.json')

    def convert(self, text_input):
        text = text_input

        input_text = texttospeech.SynthesisInput(text=text)

        # Note: the voice can also be specified by name.
        # Names of voices can be retrieved with client.list_voices().
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-US",
            name="en-US-Standard-C",
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

        return response.audio_content


if __name__ == "__main__":
    model = TranslatorModel()

    audio_input = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"\

    transcript = model.SpeechToTranscript(audio_input)
    print("Speech to text:", transcript)

    model.TranscriptToSpeech()

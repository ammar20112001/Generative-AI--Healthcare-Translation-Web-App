from google.cloud import speech


class TranslatorModel():

    def __init__(self, config=None):
        self.speech_to_transcript = SpeechToTranscript()
        self.transcript_translator = TranscriptTranslator
        self.transcript_to_speech = TranscriptToSpeech

    def SpeechToTranscript(self, audio_input):
        return self.speech_to_transcript.convert(audio_input)

    def TranscriptTranslator(self, transcript):
        pass

    def TranscriptToSpeech(self, transcript):
        pass



class SpeechToTranscript():

    def __init__(self):
        # Instantiates a client
        self.client = speech.SpeechClient.from_service_account_file('medicaltranslator-0cbcafc5cecd.json')

        
    def convert(self, audio_input):
        # The name of the audio file to transcribe
        gcs_uri = audio_input

        audio = speech.RecognitionAudio(uri=gcs_uri)

        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=16000,
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
        pass

if __name__ == "__main__":
    model = TranslatorModel()

    audio_input = "gs://cloud-samples-data/speech/brooklyn_bridge.raw"

    transcript = model.SpeechToTranscript(audio_input)
    print("Return:", transcript)
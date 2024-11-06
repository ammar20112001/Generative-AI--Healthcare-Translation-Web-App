






class TranslatorModel():

    def __init__(self, config=None, model_list=None):
        self.speech_to_transcript = model_list.SpeechToTranscript
        self.transcript_translator = model_list.TranscriptTranslator
        self.transcript_to_speech = model_list.TranscriptToSpeech

    def SpeechToTranscript(self, speech):
        pass

    def TranscriptTranslator(self, transcript):
        pass

    def TranscriptToSpeech(self, transcript):
        pass
import io
import os
import uuid

import pydub

from singleton_decorator import singleton

from TTS.utils.manage import ModelManager

from TTS.utils.synthesizer import Synthesizer

from podcast.pkg.tts.base import BaseSpeech


@singleton
class CoquiSpeech(BaseSpeech):
    DefaultModels = {
        "zh": {
            "am": "tts_models/zh-CN/baker/tacotron2-DDC-GST",
            "voc": "vocoder_models/universal/libri-tts/fullband-melgan",
            "test": "你好！",
        },

        "en": {
            "am": "tts_models/en/sam/tacotron-DDC",
            "voc": "vocoder_models/en/sam/hifigan_v2",
            "test": "Hello!",
        },

        "ja": {
            "am": "tts_models/ja/kokoro/tacotron2-DDC",
            "voc": "vocoder_models/ja/kokoro/hifigan_v1",
            "test": "こんにちは",
        },

        "de": {
            "am": "tts_models/de/thorsten/tacotron2-DCA",
            "voc": "vocoder_models/de/thorsten/fullband-melgan",
            "test": "Hallo.",
        },

        "nl": {
            "am": "tts_models/nl/mai/tacotron2-DDC",
            "voc": "vocoder_models/nl/mai/parallel-wavegan",
            "test": "Hallo.",
        },

        "fr": {
            "am": "tts_models/fr/mai/tacotron2-DDC",
            "voc": "vocoder_models/universal/libri-tts/fullband-melgan",
            "test": "Bonjour.",
        },

        "es": {
            "am": "tts_models/es/mai/tacotron2-DDC",
            "voc": "vocoder_models/universal/libri-tts/fullband-melgan",
            "test": "Hola.",
        },

        "uk": {
            "am": "tts_models/uk/mai/glow-tts",
            "voc": "vocoder_models/universal/libri-tts/fullband-melgan",
            "test": "Hello.",
        }
    }

    def __init__(self, language: str, use_cuda: bool = False):
        self.language = language
        self.use_cuda = use_cuda

        self.am = self.DefaultModels.get(language, {}).get("am", "")
        self.voc = self.DefaultModels.get(language, {}).get("voc", "")

        manager = ModelManager(None, "{0}/.ttsvm/mozilla/models".format(os.getenv("HOME")))

        self.model_path, self.config_path, self.model_item = manager.download_model(self.am)
        self.vocoder_path, self.vocoder_config_path, _ = manager.download_model(self.voc)

        self.synthesizer = Synthesizer(
            self.model_path,
            self.config_path,
            "",
            "",
            self.vocoder_path,
            self.vocoder_config_path,
            "",
            "",
            self.use_cuda
        )

    def test(self):
        test_content: str = self.DefaultModels.get(self.language, {}).get("test", "")
        for _ in self.run(test_content):
            pass

    def run(self, content: str) -> io.BytesIO:
        wav = self.synthesizer.tts(content)
        tmp_path = "/tmp/{0}.wav".format(uuid.uuid4())
        self.synthesizer.save_wav(wav, tmp_path)
        for mp3_stream in self.wav_to_mp3(tmp_path):
            yield mp3_stream
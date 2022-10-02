import io
from abc import ABCMeta, abstractmethod
import os

import pydub


class BaseSpeech:
    @abstractmethod
    def run(self, content: str):
        pass

    @classmethod
    def wav_to_mp3(cls, file_path: str) -> io.BytesIO:
        with open(file_path, "rb") as wav_file:
            mp3_content_stream = io.BytesIO()
            file = pydub.AudioSegment.from_file(wav_file).export(mp3_content_stream, format='mp3')
            yield mp3_content_stream
            mp3_content_stream.close()
            file.close()
        os.remove(file_path)

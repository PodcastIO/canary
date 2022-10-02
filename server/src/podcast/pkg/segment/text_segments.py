import re

import pysbd
from langdetect import detect, LangDetectException
from pysbd.lang.common import Common

from podcast.pkg.mq.job import QueuesManager
from podcast.pkg.segment.zh.kangxi import kangxi2zh


class LangSegment:
    def __init__(self, idx: int, language: str, content: str):
        self.idx = idx
        self.language = language
        self.content = content


class TextSegment:
    CombineLanguages = {
        "en": {
            "de":  "de",
        },
        "de": {
            "en": "de",
        }
    }

    def __init__(self, language, content):
        self.language = language
        self.content = content

    @classmethod
    def _get_zh_symbol(cls)->str:
        return "。？！，、；：「」『』‘’“”（）〔〕【】—…–．《》〈〉"

    @classmethod
    def _get_language(cls, ch):
        # https://www.jianshu.com/p/5fc54eb7ff3e
        languages_range = {
            "zh": lambda: '\u4E00' <= ch <= '\u9FFF' or ch in cls._get_zh_symbol(),
            "kangxi": lambda: kangxi2zh(ch) != "",
            "ko": lambda: '\uAC00' <= ch <= '\uD7A3',
            "ja": lambda: '\u3040' <= ch <= '\u30FF',
            "thai": lambda: '\u0E00' <= ch <= '\u0E7F',
            "en": lambda: u'a' <= ch <= u'z' or u'A' <= ch <= u'Z',
            "de": lambda: ch in ['\u00C4', '\u00E4', '\u00D6', '\u00F6', '\u00DC', '\u00FC', '\u1E9E', '\u00DF']
        }

        for language, language_range in languages_range.items():
            if language_range():
                return language

        if u'0' <= ch <= u'9':
            return "DIGIT"

        if ch in ['%', '-', '+', '/', "."]:
            return "SYMBOL"

        return ""

    @classmethod
    def _get_combine_language(cls, prev_language: str, current_language: str):
        return cls.CombineLanguages.get(prev_language, {}).get(current_language, "") and \
               current_language in QueuesManager.get_languages_can_tts()

    @classmethod
    def _justify(cls, segments):
        new_segments = []
        for (zh, s) in segments:
            new_segments.append((detect(s), s))
        return new_segments

    @classmethod
    def _justify_zh_text(cls, text: str):
        percent_numbers = re.findall("(\\d+(\\.\\d+)?\\%)", text)
        for percent_number in percent_numbers:
            replace_percent_number = "百分之" + percent_number[0].rstrip("%")
            text = text.replace(percent_number[0], replace_percent_number)

        decimal_numbers = re.findall("(\\d+\\.\\d+)", text)
        for decimal_number in set(decimal_numbers):
            replace_decimal_number = decimal_number.replace(".", "点")
            text = text.replace(decimal_number, replace_decimal_number)

        return text.strip().strip(cls._get_zh_symbol()) + "。"

    @classmethod
    def _justify_en_text(cls, text: str):
        text = text.strip()
        if not text.endswith("."):
            text += "."
        return text

    @classmethod
    def _segment_sentence(cls, sentence):
        segments = []

        segment = []
        current_segment_language = ""

        for ch in sentence:
            current_language = cls._get_language(ch)

            # unknown language to ignore, add empty character segment
            if current_language == "":
                segment.append(' ')
                continue

            if current_language == "kangxi":
                ch = kangxi2zh(ch)
                current_language = "zh"

            # digit to merge
            if current_language in ["DIGIT", "SYMBOL"]:
                segment.append(ch)
                continue

            # same language to merge
            if current_segment_language == "" or current_segment_language == current_language:
                current_segment_language = current_language
                segment.append(ch)
            else:  # different language

                combine_language = cls._get_combine_language(current_segment_language, current_language)
                if combine_language != "":  # different language can merge
                    current_segment_language = combine_language
                    segment.append(ch)
                else: # different language can't merge
                    segments.append([current_segment_language, ''.join(segment)])
                    segment = [ch]
                    current_segment_language = current_language
        if len(segment) > 0:
            segments.append([current_segment_language, ''.join(segment)])
        return segments

    def _justify_language(self, segments):
        justify_actions = {
            "zh": lambda text: self._justify_zh_text(text),
            "en": lambda text: self._justify_en_text(text),
        }

        for segment in segments:
            if segment[0] == "":
                segment[0] = self.language # unknown language to set language
            else:
                # reuse detect language to justify language type.
                try:
                    detect_language = detect(segment[1])
                except LangDetectException as e:
                    pass

                if self._get_combine_language(segment[0], detect_language) == detect_language:
                    segment[0] = detect_language

            # replace some text
            action = justify_actions.get(segment[0], None)
            if action is not None:
                segment[1] = action(segment[1])
        return segments

    @classmethod
    def _get_lang_segments(cls, segments):
        languages = set()
        segments_list = []
        for idx, segment in enumerate(segments):
            languages.add(segment[0])
            segments_list.append(LangSegment(idx, segment[0], segment[1]))
        return languages, segments_list

    def gen_lang_segments(self):
        Common.SENTENCE_BOUNDARY_REGEX = r"（(?:[^）])*）(?=\s?[A-Z])|「(?:[^」])*」(?=\s[A-Z])|\((?:[^\)]){2,}\)(?=\s[" \
                                         r"A-Z])|\'(?:[^\'])*[^,]\'(?=\s[A-Z])|\"(?:[^\"])*[^,]\"(?=\s[A-Z])|\“(?:[" \
                                         r"^\”])*[^,]\”(?=\s[A-Z])|[。．.！!?？ ]{2,}|\S.*?[，,:：。．.！!?？ȸȹ☉☈☇☄]|[。．.！!?？、，] "
        sentences = pysbd.Segmenter(language=self.language, clean=False).segment(self.content)
        segments = []
        for sentence in sentences:
            segments.extend((self._segment_sentence(sentence)))
        return self._get_lang_segments(self._justify_language(segments))

import io
import logging
import os
import time
import uuid

import numpy as np
import pydub
from singleton_decorator import singleton

import paddle
import yaml

import soundfile as sf
from paddlespeech.cli.tts.infer import pretrained_models
from paddlespeech.cli.utils import download_and_decompress
from paddlespeech.s2t.utils.dynamic_import import dynamic_import
from paddlespeech.t2s.frontend import English
from paddlespeech.t2s.frontend.zh_frontend import Frontend
from paddlespeech.t2s.modules.normalizer import ZScore
from paddlespeech.cli.tts.infer import model_alias

from yacs.config import CfgNode
from podcast.pkg.tts.base import BaseSpeech


@singleton
class PaddleSpeech(BaseSpeech):
    DefaultModels = {
        "zh": {
            "am": "tts_models/zh/csmsc/fastspeech2",
            "voc": "vocoder_models/zh/csmsc/hifigan",
        },

        "en": {
            "am": "tts_models/en/ljspeech/fastspeech2",
            "voc": "vocoder_models/en/ljspeech/hifigan",
        },
    }

    ModelDir = "{0}/.ttsvm/paddle/models".format(os.getenv("HOME"))

    def __init__(self, language: str):
        self.frontend_time = 0
        self.voc_time = 0
        self.am_time = 0
        self.language = language
        self.am = self.DefaultModels[language]["am"]
        self.voc = self.DefaultModels[language]["voc"]

        self._init_from_path()

    @classmethod
    def _download_model(cls, model_name):
        model_type, lang, dataset, model = model_name.split("/")
        model_full_name = f"{model_type}--{lang}--{dataset}--{model}"
        model_key = f"{model}_{dataset}-{lang}"
        model_item = pretrained_models[model_key]
        res_path = os.path.join(cls.ModelDir, model_full_name)
        decompressed_path = download_and_decompress(model_item, res_path)
        decompressed_path = os.path.abspath(decompressed_path)
        return decompressed_path, model_item

    def _init_from_path(self):
        am_decompress_path, am_model_item = self._download_model(self.am)
        self.am_config = os.path.join(am_decompress_path, am_model_item['config'])
        self.am_ckpt = os.path.join(am_decompress_path, am_model_item['ckpt'])
        self.am_stat = os.path.join(am_decompress_path, am_model_item['speech_stats'])
        self.phones_dict = os.path.join(am_decompress_path, am_model_item['phones_dict'])

        # for speedyspeech
        self.tones_dict = None
        if 'tones_dict' in am_model_item:
            self.tones_dict = os.path.join(am_decompress_path, am_model_item['tones_dict'])

        # for multi speaker fastspeech2
        self.speaker_dict = None
        if 'speaker_dict' in am_model_item:
            self.speaker_dict = os.path.join(am_decompress_path, am_model_item['speaker_dict'])

        voc_decompress_path, voc_model_item = self._download_model(self.voc)
        self.voc_res_path = voc_decompress_path
        self.voc_config = os.path.join(voc_decompress_path, voc_model_item['config'])
        self.voc_ckpt = os.path.join(voc_decompress_path, voc_model_item['ckpt'])
        self.voc_stat = os.path.join(voc_decompress_path, voc_model_item['speech_stats'])

        # Init body.
        with open(self.am_config) as f:
            self.am_config = CfgNode(yaml.safe_load(f))
        with open(self.voc_config) as f:
            self.voc_config = CfgNode(yaml.safe_load(f))

        with open(self.phones_dict, "r") as f:
            phn_id = [line.strip().split() for line in f.readlines()]
        vocab_size = len(phn_id)
        print("vocab_size:", vocab_size)

        tone_size = None
        if self.tones_dict:
            with open(self.tones_dict, "r") as f:
                tone_id = [line.strip().split() for line in f.readlines()]
            tone_size = len(tone_id)
            print("tone_size:", tone_size)

        spk_num = None
        if self.speaker_dict:
            with open(self.speaker_dict, 'rt') as f:
                spk_id = [line.strip().split() for line in f.readlines()]
            spk_num = len(spk_id)
            print("spk_num:", spk_num)

        # frontend
        if self.language == 'zh':
            self.frontend = Frontend(
                phone_vocab_path=self.phones_dict,
                tone_vocab_path=self.tones_dict)

        elif self.language == 'en':
            self.frontend = English(phone_vocab_path=self.phones_dict)
        print("frontend done!")

        # acoustic model
        odim = self.am_config.n_mels
        am_name = self.am.split("/")[-1]
        am_class = dynamic_import(am_name, model_alias)
        am_inference_class = dynamic_import(am_name + '_inference', model_alias)

        if am_name == 'fastspeech2':
            am = am_class(
                idim=vocab_size,
                odim=odim,
                spk_num=spk_num,
                **self.am_config["model"])
        elif am_name == 'speedyspeech':
            am = am_class(
                vocab_size=vocab_size,
                tone_size=tone_size,
                **self.am_config["model"])

        am.set_state_dict(paddle.load(self.am_ckpt)["main_params"])
        am.eval()
        am_mu, am_std = np.load(self.am_stat)
        am_mu = paddle.to_tensor(am_mu)
        am_std = paddle.to_tensor(am_std)
        am_normalizer = ZScore(am_mu, am_std)
        self.am_inference = am_inference_class(am_normalizer, am)
        self.am_inference.eval()
        print("acoustic model done!")

        # vocoder
        voc_name = self.voc.split("/")[-1]
        voc_class = dynamic_import(voc_name, model_alias)
        voc_inference_class = dynamic_import(voc_name + '_inference',
                                             model_alias)
        voc = voc_class(**self.voc_config["generator_params"])
        voc.set_state_dict(paddle.load(self.voc_ckpt)["generator_params"])
        voc.remove_weight_norm()
        voc.eval()
        voc_mu, voc_std = np.load(self.voc_stat)
        voc_mu = paddle.to_tensor(voc_mu)
        voc_std = paddle.to_tensor(voc_std)
        voc_normalizer = ZScore(voc_mu, voc_std)
        self.voc_inference = voc_inference_class(voc_normalizer, voc)
        self.voc_inference.eval()
        print("voc done!")

    @paddle.no_grad()
    def infer(self, text: str):
        """
        Model inference and result stored in self.output.
        """
        am_name = self.am[:self.am.rindex('_')]
        am_dataset = self.am[self.am.rindex('_') + 1:]
        get_tone_ids = False
        merge_sentences = False
        frontend_st = time.time()
        if am_name == 'speedyspeech':
            get_tone_ids = True
        if self.language == 'zh':
            input_ids = self.frontend.get_input_ids(
                text,
                merge_sentences=merge_sentences,
                get_tone_ids=get_tone_ids)
            phone_ids = input_ids["phone_ids"]
            if get_tone_ids:
                tone_ids = input_ids["tone_ids"]
        elif self.language == 'en':
            input_ids = self.frontend.get_input_ids(
                text, merge_sentences=merge_sentences)
            phone_ids = input_ids["phone_ids"]
        else:
            print("lang should in {'zh', 'en'}!")
        self.frontend_time = time.time() - frontend_st

        self.am_time = 0
        self.voc_time = 0
        flags = 0
        for i in range(len(phone_ids)):
            am_st = time.time()
            part_phone_ids = phone_ids[i]
            # am
            if am_name == 'speedyspeech':
                part_tone_ids = tone_ids[i]
                mel = self.am_inference(part_phone_ids, part_tone_ids)
            # fastspeech2
            else:
                # multi speaker
                if am_dataset in {"aishell3", "vctk"}:
                    mel = self.am_inference(
                        part_phone_ids, spk_id=paddle.to_tensor(0))
                else:
                    mel = self.am_inference(part_phone_ids)
            self.am_time += (time.time() - am_st)
            # voc
            return self.voc_inference(mel)

    def run(self, content: str) -> bytes:
        try:
            wav = self.infer(content)
            tmp_path = "/tmp/{0}.wav".format(uuid.uuid4())
            sf.write(tmp_path, wav.numpy(), samplerate=self.am_config.fs)
            for mp3_stream in self.wav_to_mp3(tmp_path):
                yield mp3_stream
        except Exception as ex:
            print(self.language, content)
            logging.exception(ex)
            return None


from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple, Union

import torch
import torch.nn as nn
from fairseq2.assets.card import AssetCard
from fairseq2.data import Collater
from fairseq2.data.audio import AudioDecoder, WaveformToFbankConverter
from fairseq2.data.text.text_tokenizer import TextTokenizer
from fairseq2.data.typing import StringLike
from fairseq2.generation import SequenceToTextOutput, SequenceGeneratorOptions
from fairseq2.memory import MemoryBlock
from fairseq2.typing import DataType, Device
from torch import Tensor
from enum import Enum, auto
from seamless_communication.models.inference.ngram_repeat_block_processor import (
    NGramRepeatBlockProcessor,
)

from seamless_communication.models.unity import (
    UnitTokenizer,
    UnitYGenerator,
    UnitYModel,
    load_unity_model,
    load_unity_text_tokenizer,
    load_unity_unit_tokenizer,
)
from seamless_communication.models.unity.generator import SequenceToUnitOutput
from seamless_communication.models.vocoder import load_vocoder_model, Vocoder



from seamless_communication.models.streaming.agents import (
    SileroVADAgent,
    TestTimeWaitKS2TVAD,
    TestTimeWaitKUnityV1M4T
)

### From test_pipeline
import math
import soundfile
from argparse import Namespace, ArgumentParser
from simuleval.data.segments import SpeechSegment, EmptySegment
from simuleval.utils import build_system_from_dir
from pathlib import Path
import numpy as np

class AudioFrontEnd:
    def __init__(self, wav_file, segment_size) -> None:
        self.samples, self.sample_rate = soundfile.read(wav_file)
        # print(len(self.samples), self.samples[:100])
        self.samples = self.samples.tolist()
        self.segment_size = segment_size
        self.step = 0
    def send_segment(self):
        """
        This is the front-end logic in simuleval instance.py
        """
        num_samples = math.ceil(self.segment_size / 1000 * self.sample_rate)
        print("self.segment_size", self.segment_size)
        print('num_samples is', num_samples)
        print('self.sample_rate is', self.sample_rate)
        if self.step < len(self.samples):
            if self.step + num_samples >= len(self.samples):
                samples = self.samples[self.step :]
                is_finished = True
            else:
                samples = self.samples[self.step : self.step + num_samples]
                is_finished = False
            self.step = min(self.step + num_samples, len(self.samples))
            # print("len(samples) is", len(samples))
            # import pdb
            # pdb.set_trace()
            segment = SpeechSegment(
                index=self.step / self.sample_rate * 1000,
                content=samples,
                sample_rate=self.sample_rate,
                finished=is_finished,
            )
        else:
            # Finish reading this audio
            segment = EmptySegment(
                index=self.step / self.sample_rate * 1000,
                finished=True,
            )
        return segment



def load_model_for_inference(
    load_model_fn: Callable[..., nn.Module],
    model_name_or_card: Union[str, AssetCard],
    device: Device,
    dtype: DataType,
) -> nn.Module:
    model = load_model_fn(model_name_or_card, device=device, dtype=dtype)
    model.eval()
    return model

class SimulevalTranscoder:
    # def __init__(self, agent, sample_rate, debug, buffer_limit):
    def __init__(self):
        print("MDUPPES in here", SileroVADAgent, TestTimeWaitKS2TVAD)
        device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

        device = "cpu"
        print("DEVICE", device)
        model_name_or_card="seamlessM4T_medium"
        vocoder_name_or_card="vocoder_36langs"
        # dtype=torch.float16,
        # For CPU Mode need to use 32, float16 causes errors downstream
        dtype=dtype=torch.float32

        model: UnitYModel = load_model_for_inference(
            load_unity_model, model_name_or_card, device, dtype
        )


        print(model, type(model))
        parser = ArgumentParser()
        source_segment_size = 320  # milliseconds
        audio_frontend = AudioFrontEnd(
            wav_file="/checkpoint/mduppes/samples/marta.wav",
            segment_size=source_segment_size,
        )

        # mostly taken from S2S first agent: OnlineFeatureExtractorAgent defaults
        SHIFT_SIZE = 10
        WINDOW_SIZE = 25
        SAMPLE_RATE = 16000
        FEATURE_DIM = 80

        # args and convert to namespace so it can be accesed via .
        args = {
            "shift_size": SHIFT_SIZE,
            "window_size": WINDOW_SIZE,
            "sample_rate": audio_frontend.sample_rate,
            "feature_dim": 160, # from Wav2Vec2Frontend
            "denormalize": False, # not sure..
            "global_stats": None, # default file path containing cmvn stats..
        }
        print(args)
        args = Namespace(**args)

        pipeline = TestTimeWaitKUnityV1M4T(model, args)
        system_states = pipeline.build_states()
        print('system states')
        print(system_states)
        input_segment = np.empty(0, dtype=np.int16)
        segments = []
        while True:
            speech_segment = audio_frontend.send_segment()
            input_segment = np.concatenate((input_segment, np.array(speech_segment.content)))
            # Translation happens here
            output_segment = pipeline.pushpop(speech_segment, system_states)
            print('pushpop result')
            print(output_segment)
            if output_segment.finished:
                segments.append(input_segment)
                input_segment = np.empty(0, dtype=np.int16)
                print("Resetting states")
                for state in system_states:
                    state.reset()
            if speech_segment.finished:
                break
        # The VAD-segmented samples from the full input audio
        for i, seg in enumerate(segments):
            with soundfile.SoundFile(
                Path("/checkpoint/mduppes/samples") / f"marta_{i}.wav",
                mode="w+",
                format="WAV",
                samplerate=16000,
                channels=1,
            ) as f:
                f.seek(0, soundfile.SEEK_END)
                f.write(seg)


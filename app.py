from __future__ import annotations

import gradio as gr
import numpy as np

import asyncio
from simuleval_transcoder import SimulevalTranscoder, logger

import time
from simuleval.utils.agent import build_system_from_dir
import torch


language_code_to_name = {
    "cmn": "Mandarin Chinese",
    "deu": "German",
    "eng": "English",
    "fra": "French",
    "spa": "Spanish",
}
S2ST_TARGET_LANGUAGE_NAMES = language_code_to_name.values()
LANGUAGE_NAME_TO_CODE = {v: k for k, v in language_code_to_name.items()}

DEFAULT_TARGET_LANGUAGE = "English"


def build_agent(model_path, config_name=None):
    agent = build_system_from_dir(
        model_path, config_name=config_name,
    )
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    agent.to(device, fp16=True)

    return agent

agent = build_agent("models", "vad_s2st_sc_24khz_main.yaml")
transcoder = SimulevalTranscoder(
    agent,
    sample_rate=48_000,
    debug=False,
    buffer_limit=1,
)

def start_recording():
    logger.debug(f"start_recording: starting transcoder")
    transcoder.reset_states()
    transcoder.close = False
    transcoder.start()

def stop_recording():
    transcoder.close = True

class MyState:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.close = False


s = MyState()

def process_incoming_bytes(audio):
    logger.debug(f"process_bytes: incoming audio")
    sample_rate, data = audio
    transcoder.process_incoming_bytes(data.tobytes(), 'eng', sample_rate)
    s.queue.put_nowait(audio)



def get_buffered_output():

    speech_and_text_output =  transcoder.get_buffered_output()
    if speech_and_text_output is None:
        logger.debug("No output from transcoder.get_buffered_output()")
        return None, None, None

    logger.debug(f"We DID get output from the transcoder!")

    text = None
    speech = None

    if speech_and_text_output.speech_samples:
        speech = (speech_and_text_output.speech_sample_rate, speech_and_text_output.speech_samples)

    if speech_and_text_output.text:
        text = speech_and_text_output.text
        if speech_and_text_output.final:
            text += "\n"

    return speech, text, speech_and_text_output.final

from scipy.io.wavfile import write as scipy_write
def streaming_input_callback():
    final = False
    max_wait_s = 15
    wait_s = 0
    translated_text_state = ""
    sample_rate = 24000
    while not transcoder.close:
        translated_wav_segment, translated_text, final = get_buffered_output()

        if translated_wav_segment is None and translated_text is None:
            time.sleep(0.3)
            wait_s += 0.3
            if wait_s >= max_wait_s:
                transcoder.close = True
            continue
        wait_s = 0
        if translated_wav_segment is not None:
            sample_rate, audio_bytes = translated_wav_segment
            print("output sample rate", sample_rate)
            translated_wav_segment = sample_rate, np.array(audio_bytes)
        else:
            translated_wav_segment = sample_rate, np.empty(0, dtype=np.int16)

        if translated_text is not None:
            translated_text_state += " | " + str(translated_text)

        stream_output_text = translated_text_state
        if translated_text is not None:
            print("translated:", translated_text_state)
        yield [
            translated_wav_segment,
            stream_output_text,
            translated_text_state,
        ]


def streaming_callback_dummy():
    i = 0
    out_text = ""
    while not transcoder.close:
        if s.queue.empty():
            yield (
                (48000, np.empty(0, dtype=np.int16)), out_text, out_text
            )
            time.sleep(0.3)
        else:
            i += 1
            out_text += " | " + str(i)
            print(out_text)
            audio = s.queue.get_nowait()
            if i == 0:
                print(audio[0], type(audio[1]))
            s.queue.task_done()
            yield audio, out_text, out_text

def clear():
    logger.debug(f"Clearing State")
    return [bytes(), ""]


def blocks():
    with gr.Blocks() as demo:

        with gr.Row():
            # TODO: add target language switching
            target_language = gr.Dropdown(
                label="Target language",
                choices=S2ST_TARGET_LANGUAGE_NAMES,
                value=DEFAULT_TARGET_LANGUAGE,
            )

        translated_text_state = gr.State("")

        input_audio = gr.Audio(
            label="Input Audio",
            sources=["microphone"],
            streaming=True,
        )

        output_translation_segment = gr.Audio(
            label="Translated audio segment",
            autoplay=True,
            streaming=True,
        )

        # Output text segment
        stream_output_text = gr.Textbox(label="Translated text")

        input_audio.clear(
            clear, None, [output_translation_segment, translated_text_state]
        )
        input_audio.start_recording(
            clear, None, [output_translation_segment, translated_text_state]
        ).then(
            start_recording
        ).then(
            # TODO: streaming speech autoplay works fine with streaming_callback_dummy,
            # but speech output from streaming_input_callback has a huge delay
            # when comparing print/debugging logs vs. output speech
            # TODO: text output works fine with one output, but is not
            # updating when output is both text + speech
            # streaming_callback_dummy,
            streaming_input_callback,
            None,
            [
                output_translation_segment,
                stream_output_text,
                translated_text_state,
            ]
        )
        input_audio.stop_recording(
            stop_recording
        )
        input_audio.stream(
            # TODO: *only when streaming speech output* about half the time 
            # there is some race condition in gradio where process_incoming_bytes
            # stops getting called once the first speech chunk is yield-ed 
            # in streaming_input_callback (or streaming_callback_dummy)
            process_incoming_bytes, [input_audio], None
        )

    demo.launch(server_port=6010)

blocks()

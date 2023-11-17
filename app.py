from __future__ import annotations

import os

import gradio as gr
import numpy as np
import torch
import torchaudio

from simuleval_transcoder import *

from pydub import AudioSegment
import time
from time import sleep

from seamless_communication.cli.streaming.agents.tt_waitk_unity_s2t_m4t import (
    TestTimeWaitKUnityS2TM4T,
)

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

# TODO: Update this so it takes in target langs from input, refactor sample rate
transcoder = SimulevalTranscoder(
    sample_rate=48_000,
    debug=False,
    buffer_limit=1,
)

def start_recording():
    logger.debug(f"start_recording: starting transcoder")
    transcoder.start()


def translate_audio_segment(audio):
    logger.debug(f"translate_audio_segment: incoming audio")
    sample_rate, data = audio

    transcoder.process_incoming_bytes(data.tobytes(), 'eng', sample_rate)

    speech_and_text_output =  transcoder.get_buffered_output()
    if speech_and_text_output is None:
        logger.debug("No output from transcoder.get_buffered_output()")
        return None, None

    logger.debug(f"We DID get output from the transcoder! {speech_and_text_output}")

    text = None
    speech = None

    if speech_and_text_output.speech_samples:
        speech = (speech_and_text_output.speech_samples, speech_and_text_output.speech_sample_rate)

    if speech_and_text_output.text:
        text = speech_and_text_output.text
        if speech_and_text_output.final:
            text += "\n"

    return speech, text

def streaming_input_callback(
    audio_file, translated_audio_bytes_state, translated_text_state
):
    translated_wav_segment, translated_text = translate_audio_segment(audio_file)
    logger.debug(f'translated_audio_bytes_state {translated_audio_bytes_state}')
    logger.debug(f'translated_wav_segment {translated_wav_segment}')

    # TODO: accumulate each segment to provide a continuous audio segment

    if translated_wav_segment is not None:
        sample_rate, audio_bytes = translated_wav_segment
        audio_np_array = np.frombuffer(audio_bytes, dtype=np.float32, count=3)


        # combine translated wav
        if type(translated_audio_bytes_state) is not tuple:
            translated_audio_bytes_state = (sample_rate, audio_np_array)
            # translated_audio_bytes_state = np.array([])
        else:

            translated_audio_bytes_state = (translated_audio_bytes_state[0], np.append(translated_audio_bytes_state[1], translated_wav_segment[1]))

    if translated_text is not None:
        translated_text_state += " | " + str(translated_text)

    # most_recent_input_audio_segment = (most_recent_input_audio_segment[0], np.append(most_recent_input_audio_segment[1], audio_file[1]))

    # Not necessary but for readability.
    most_recent_input_audio_segment = audio_file
    translated_wav_segment = translated_wav_segment
    output_translation_combined = translated_audio_bytes_state
    stream_output_text = translated_text_state
    return [
        most_recent_input_audio_segment,
        translated_wav_segment,
        output_translation_combined,
        stream_output_text,
        translated_audio_bytes_state,
        translated_text_state,
    ]


def clear():
    logger.debug(f"Clearing State")
    return [bytes(), ""]


def blocks():
    with gr.Blocks() as demo:

        with gr.Row():
            # Hook this up once supported
            target_language = gr.Dropdown(
                label="Target language",
                choices=S2ST_TARGET_LANGUAGE_NAMES,
                value=DEFAULT_TARGET_LANGUAGE,
            )

        translated_audio_bytes_state = gr.State(None)
        translated_text_state = gr.State("")

        input_audio = gr.Audio(
            label="Input Audio",
            # source="microphone", # gradio==3.41.0
            sources=["microphone"], # new gradio seems to call this less often...
            streaming=True,
        )

        # input_audio = gr.Audio(
        #     label="Input Audio",
        #     type="filepath",
        #     source="microphone",
        #     streaming=True,
        # )

        most_recent_input_audio_segment = gr.Audio(
            label="Recent Input Audio Segment segments",
            # format="bytes",
            streaming=True
        )

        # Force translate
        stream_as_bytes_btn = gr.Button("Force translate most recent recording segment (ask for model output)")
        output_translation_segment = gr.Audio(
            label="Translated audio segment",
            autoplay=False,
            streaming=True,
            type="numpy",
        )

        output_translation_combined = gr.Audio(
            label="Translated audio combined",
            autoplay=False,
            streaming=True,
            type="numpy",
        )

        # Could add output text segment
        stream_output_text = gr.Textbox(label="Translated text")

        stream_as_bytes_btn.click(
            streaming_input_callback,
            [input_audio, translated_audio_bytes_state, translated_text_state],
            [
                most_recent_input_audio_segment,
                output_translation_segment,
                output_translation_combined,
                stream_output_text,
                translated_audio_bytes_state,
                translated_text_state,
            ],
        )

        # input_audio.change(
        #     streaming_input_callback,
        #     [input_audio, translated_audio_bytes_state, translated_text_state],
        #     [
        #         most_recent_input_audio_segment,
        #         output_translation_segment,
        #         output_translation_combined,
        #         stream_output_text,
        #         translated_audio_bytes_state,
        #         translated_text_state,
        #     ],
        # )

        input_audio.stream(
            streaming_input_callback,
            [input_audio, translated_audio_bytes_state, translated_text_state],
            [
                most_recent_input_audio_segment,
                output_translation_segment,
                output_translation_combined,
                stream_output_text,
                translated_audio_bytes_state,
                translated_text_state,
            ],
        )

        input_audio.start_recording(
            start_recording,
        )

        input_audio.clear(
            clear, None, [translated_audio_bytes_state, translated_text_state]
        )
        input_audio.start_recording(
            clear, None, [translated_audio_bytes_state, translated_text_state]
        )

    demo.queue().launch()

blocks()

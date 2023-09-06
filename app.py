from __future__ import annotations

import os

import gradio as gr
import numpy as np
import torch
import torchaudio
from seamless_communication.models.inference.translator import Translator


from m4t_app import *

from pydub import AudioSegment
import time
from time import sleep

# m4t_demo()

USE_M4T = True


def translate_audio_file_segment(audio_file):
    print("translate_m4t state")

    return predict(
        task_name="S2ST",
        audio_source="microphone",
        input_audio_mic=audio_file,
        input_audio_file=None,
        input_text="",
        source_language="English",
        target_language="Portuguese",
    )


def translate_m4t_callback(
    audio_file, translated_audio_bytes_state, translated_text_state
):
    translated_wav_segment, translated_text = translate_audio_file_segment(audio_file)
    print('translated_audio_bytes_state', translated_audio_bytes_state)
    print('translated_wav_segment', translated_wav_segment)

    # combine translated wav into larger..
    if type(translated_audio_bytes_state) is not tuple:
        translated_audio_bytes_state = translated_wav_segment
    else:

        translated_audio_bytes_state = (translated_audio_bytes_state[0], np.append(translated_audio_bytes_state[1], translated_wav_segment[1]))

    # translated_wav_segment[1]


    translated_text_state += " | " + str(translated_text)
    return [
        audio_file,
        translated_wav_segment,
        translated_audio_bytes_state,
        translated_text_state,
        translated_audio_bytes_state,
        translated_text_state,
    ]


def clear():
    print("Clearing State")
    return [bytes(), ""]


def blocks():
    with gr.Blocks() as demo:
        translated_audio_bytes_state = gr.State(None)
        translated_text_state = gr.State("")

        # input_audio = gr.Audio(label="Input Audio", type="filepath", format="mp3")
        if USE_M4T:
            input_audio = gr.Audio(
                label="Input Audio",
                type="filepath",
                source="microphone",
                streaming=True,
            )
        else:
            input_audio = gr.Audio(
                label="Input Audio",
                type="filepath",
                format="mp3",
                source="microphone",
                streaming=True,
            )

        most_recent_input_audio_segment = gr.Audio(
            label="Recent Input Audio Segment segments", format="bytes", streaming=True
        )
        # TODO: Should add combined input audio segments...

        stream_as_bytes_btn = gr.Button("Translate most recent recording segment")

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
            translate_m4t_callback,
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

        input_audio.change(
            translate_m4t_callback,
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
        # input_audio.change(stream_bytes, [input_audio, translated_audio_bytes_state, translated_text_state], [most_recent_input_audio_segment, stream_output_text, translated_audio_bytes_state, translated_text_state])
        # input_audio.change(lambda input_audio: recorded_audio, [input_audio], [recorded_audio])
        input_audio.clear(
            clear, None, [translated_audio_bytes_state, translated_text_state]
        )
        input_audio.start_recording(
            clear, None, [translated_audio_bytes_state, translated_text_state]
        )

    demo.queue().launch()


# if __name__ == "__main__":
blocks()

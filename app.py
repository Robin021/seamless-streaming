from __future__ import annotations

import os

import gradio as gr
import numpy as np
import torch
import torchaudio
from seamless_communication.models.inference.translator import Translator

from transformers import pipeline

p = pipeline("automatic-speech-recognition")

from pydub import AudioSegment
import time
from time import sleep


def transcribe(audio, state=""):
    # sleep(2)
    print('state', state)
    text = p(audio)["text"]
    state += text + " "
    return state

def blocks():
    with gr.Blocks() as demo:
        total_audio_bytes_state = gr.State(bytes())
        total_text_state = gr.State("")

        # input_audio = gr.Audio(label="Input Audio", type="filepath", format="mp3")
        input_audio = gr.Audio(label="Input Audio", type="filepath", format="mp3", source="microphone", streaming=True)
        with gr.Row():
            with gr.Column():
                stream_as_bytes_btn = gr.Button("Stream as Bytes")
                stream_as_bytes_output = gr.Audio(format="bytes", streaming=True)
                stream_output_text = gr.Textbox(label="Translated text")


                def stream_bytes(audio_file, total_audio_bytes_state, total_text_state):
                    chunk_size = 30000

                    print(f"audio_file {audio_file}, size {os.path.getsize(audio_file)}")
                    with open(audio_file, "rb") as f:

                        while True:
                            chunk = f.read(chunk_size)
                            if chunk:
                                total_audio_bytes_state += chunk
                                print('yielding chunk', len(chunk))
                                print('total audio bytes', len(total_audio_bytes_state))
                                print(f"Text state: {total_text_state}")

                                # This does the whole thing every time
                                # total_text = transcribe(chunk, "")
                                # yield total_audio_bytes_state, total_text, total_audio_bytes_state, total_text_state

                                # This translates just the new part every time
                                total_text_state = transcribe(chunk, total_text_state)
                                total_text = total_text_state
                                # total_text = transcribe(chunk, total_text)
                                yield total_audio_bytes_state, total_text, total_audio_bytes_state, total_text_state
                                # sleep(3)
                            else:
                                break
                def clear():
                    print('clearing')
                    return [bytes(), ""]

                stream_as_bytes_btn.click(stream_bytes, [input_audio, total_audio_bytes_state, total_text_state], [stream_as_bytes_output, stream_output_text, total_audio_bytes_state, total_text_state])

        input_audio.change(stream_bytes, [input_audio, total_audio_bytes_state, total_text_state], [stream_as_bytes_output, stream_output_text, total_audio_bytes_state, total_text_state])
        input_audio.clear(clear, None, [total_audio_bytes_state, total_text_state])
        input_audio.start_recording(clear, None, [total_audio_bytes_state, total_text_state])


    demo.queue().launch()


# if __name__ == "__main__":
blocks()

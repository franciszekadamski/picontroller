#!/usr/bin/python3

import io
import os
import tempfile

from pydub import AudioSegment
import streamlit as st
import whisper

import llm_interfaces
import speak


cli_picontroller_path = f'{os.environ["PICONTROLLER_PROJECT_PATH"]}/cli_picontroller'


@st.cache_data
def get_cli_output_table():
    return llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')


@st.cache_resource
def load_model():
    return llm_interfaces.HumanLanguageInterface(
        model_path=f'{os.environ["HOME"]}/picontroller_llm_models/qwen2.5-1.5b-instruct-q6_k.gguf'
    )


@st.cache_resource
def load_whisper_model():
    return whisper.load_model('tiny.en')


def execute_request(user_request_text):
    get_output = get_cli_output_table()
    response, _ = hli(
        user_request_text,
        (
            'You are an interface between human user and a cli. '
            'In order to make the cli work, your answer has to be only the name of the parameter followed by one space and a float value. '
            'Keys from the following table are the only valid answers: '
            f'{get_output}'
            'No other answer is valid'
        )
    )
    command = f'{cli_picontroller_path} set {response}'
    llm_interfaces.execute_linux_command(command)
    return llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
    # speak.speak_aloud(output)


def speech_to_text(audio_input):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_input.getvalue())
        tmp_path = tmp_file.name

    return whisper.transcribe(tmp_path)['text']



hli = load_model()
whisper = load_whisper_model()

user_input = st.text_input('User request to the system', key='user_request')
user_voice_input = st.audio_input('Voice command', sample_rate=48000)

if user_voice_input:
    with st.spinner("Transcribing..."):
        user_input = speech_to_text(user_voice_input) 
        if user_input:
            st.success(f"Voice transcription:\n{user_input}")

if user_input:
    user_input = user_input.lower()
    if user_input.startswith('command'):
        if len(user_input.split(' ')) >= 2:
            store_key = user_input.split(' ')[1]
            if store_key == 'get':
                store_table = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
            elif store_key == 'set':
                if len(user_input.split(' ')) >= 4:
                    store_key = user_input.split(' ')[2]
                    store_value = user_input.split(' ')[3]
                    store_table = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} set {store_key} {store_value}')
                else:
                    st.warning('commands set requires key and value')
                    store_table = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
            else:
                st.warning('available commands are set and get')
                store_table = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
        else:
            st.warning('no command follows')
            store_table = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
    else:
        store_table = execute_request(user_input)
    st.code(store_table)

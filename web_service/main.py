#!/usr/bin/python3

import os

import streamlit as st
import llm_interfaces
import speak

cli_picontroller_path = f'{os.environ["PICONTROLLER_PROJECT_PATH"]}/cli_picontroller'

@st.cache_resource
def load_model():
    return llm_interfaces.HumanLanguageInterface(
        model_path=f'{os.environ["HOME"]}/picontroller_llm_models/qwen2.5-1.5b-instruct-q6_k.gguf'
    )


def execute_request(user_request_text):
    get_output = llm_interfaces.execute_linux_command(f'{cli_picontroller_path} get')
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


hli = load_model()


user_input = st.text_input('User request to the system', key='user_request')
audio_input = st.audio_input('Voice command')

if user_input:
    store_table = execute_request(user_input)
    st.code(store_table)

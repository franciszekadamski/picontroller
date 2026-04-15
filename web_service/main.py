#!/usr/bin/python3

import io
import os

from pydub import AudioSegment
import streamlit as st
import speech_recognition as sr

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


def speech_to_text(audio_file):
    """
    Converts Streamlit audio_input to text using Google Speech Recognition.
    """
    recognizer = sr.Recognizer()
    
    try:
        # IMPORTANT: Streamlit widgets reuse the same file object in memory.
        # We must reset the pointer to the start or the recognizer sees 0 bytes.
        audio_file.seek(0)
        
        # Read the file into an AudioFile object that sr understands
        with sr.AudioFile(audio_file) as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5) 

            # record() reads the entire duration of the audio_input
            audio_data = recognizer.record(source)

            # Perform the recognition
            # Note: This requires an internet connection for Google's API
            text = recognizer.recognize_google(audio_data, language="en-US")
            return text.lower()

    except sr.UnknownValueError:
        # This happens if the user recorded silence or noise
        st.warning("Speech recognition could not understand the audio.")
    except sr.RequestError as e:
        # This happens if the Pi loses internet connection
        st.error(f"Could not request results from Google; {e}")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    
    return None



hli = load_model()


user_input = st.text_input('User request to the system', key='user_request')
user_voice_input = st.audio_input('Voice command', sample_rate=48000)

if user_voice_input:
    user_input = speech_to_text(user_voice_input)
    with st.spinner("Transcribing..."):
        user_input = speech_to_text(user_voice_input) 
        if user_input:
            st.success(f"Recognized: {user_input}")

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


def speech_to_text(voice_input):
    speech_recognizer = sr.Recognizer()

    try:
        with voice_input as source:
            r.adjust_for_ambient_noise(source, duration=0.2)
            audio = r.listen(source)
            text = r.recognize_google(audio)
            text = text.lower()  
            
    except speech_recognizer.RequestError as e:
        print("Could not request results; {0}".format(e))

    except speech_recognizer.UnknownValueError:
        print("Could not understand audio")


import json
import time

import streamlit
import zmq


CONFIGURATION_FILE_PATH = 'configuration_files/configuration.json'

streamlit.title('Light and humidity contoller')

@streamlit.cache_resource
def get_zmq_socket():
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.setsockopt(zmq.RCVTIMEO, 5000)
    socket.setsockopt(zmq.SNDTIMEO, 5000)
    socket.connect('tcp://localhost:5555')
    return socket


def send_and_receive(payload):
    try:
        socket.send_json(payload)
        return socket.recv_json()
    except zmq.ZMQError:
        streamlit.error('ZMQ Sync Error. Resetting connection...')
        socket.close()
        # streamlit.cache_resource.clear()
        return None


@streamlit.fragment(run_every=3)
def zmq_data_store_monitor():
    global zmq_data_store
    data = send_and_receive({'action': 'get'})
    if data:
        zmq_data_store = data
        streamlit.write(zmq_data_store)
        streamlit.caption(f'Last update: {time.strftime("%H:%M:%S")}')


socket = get_zmq_socket()
with open(CONFIGURATION_FILE_PATH, 'r') as file:
    zmq_data_store = json.loads(file.read())['zmq_data_store']

zmq_data_store_monitor()

streamlit.divider()

if streamlit.button('Apply changes'):
    payload = {
        'action': 'set',
        'data': zmq_data_store
    }
    updated_zmq_data_store = send_and_receive(payload)
    if updated_zmq_data_store == zmq_data_store:
        streamlit.success('Zmq data store updated!')

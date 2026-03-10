import json
import time

import textual
from textual import app, containers, events, widgets
import zmq


CONFIGURATION_FILE_PATH = 'configuration_files/configuration.json'
with open('hub_ip.json', 'r') as file:
    HUB_IP = json.loads(file.read())['hub_ip']





class MainApp(app.App):
    CSS_PATH = 'main.tcss'

    def compose(self) -> app.ComposeResult:
        yield widgets.Header()
        yield containers.VerticalScroll(
            containers.Container(
                containers.Horizontal(
                    widgets.DataTable(id='datastorelist'),
                    containers.Vertical(
                        widgets.Label(' New value for selected row\n'),
                        widgets.Input(
                            placeholder='Input value',
                            type='text',
                            validate_on=['submitted']
                        ),
                        widgets.Button('Update values'),
                        id='inputfield'
                    )
                )
            )
        )
        yield widgets.Footer()

    
    @textual.on(widgets.Input.Submitted)
    def update_value(self, input_value: str):
        key = self.rows[self.table.cursor_coordinate.row][0]
        new_rows = self.client('set', key, input_value.value)[1:]
        for row_index in range(len(new_rows)):
            self.table.update_cell_at(
                textual.coordinate.Coordinate(row=row_index, column=1),
                new_rows[row_index][1]
            )
        self.notify(f'Successfully sent request for setting value {input_value.value} to key {key}') 
        self.notify(f'Values in the table updated') 


    def on_button_pressed(self, event: widgets.Button.Pressed) -> None:
        new_rows = self.client('get')[1:]
        for row_index in range(len(new_rows)):
            self.table.update_cell_at(
                textual.coordinate.Coordinate(row=row_index, column=1),
                new_rows[row_index][1]
            )
        self.notify(f'Values in the table updated') 


    def on_mount(self) -> None:
        self.socket = self.get_zmq_socket()
        self.title = 'Picontroller TUI'

        self.rows = [('Key', 'Value')]
        self.table = self.query_one(widgets.DataTable)
        self.table.cursor_type = 'row'
        self.table.zebra_stripes = False
        self.table.add_columns(*self.rows[0])

        self.rows = self.client('get')[1:]
        self.table.add_rows(self.rows)


    def get_zmq_socket(self):
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.setsockopt(zmq.RCVTIMEO, 5000)
        socket.setsockopt(zmq.SNDTIMEO, 5000)
        socket.connect(f'tcp://{HUB_IP}:5555')
        return socket
    
    
    def send_and_receive(self, payload):
        try:
            self.socket.send_json(payload)
            return self.socket.recv_json()
        except zmq.ZMQError:
            self.socket.close()
            return None
    
    
    def data_to_rows(self, data):
        rows = [('Key', 'Value')]
        for key, value in data.items():
            rows.append((key, value))
        return rows
    
     
    def client(self, action, key=None, value=None):
        if action not in ['get', 'set', 'save']:
            print(f'possible actions are: get, set, save')
            return
        data = self.send_and_receive({'action': 'get'})
        if not data:
            raise Exception('Could not read data')
    
        if action == 'get':
            return self.data_to_rows(data)
        elif action == 'set':
            try:
                data[key] = float(value)
            except ValueError:
                data[key] = str(value)
            payload = {
                'action': 'set',
                'data': data
            }
            data = self.send_and_receive(payload)
            return self.data_to_rows(data)
        elif action == 'save':
            data = self.send_and_receive({'action': 'save'})
            return self.data_to_rows(data)
        



if __name__ == "__main__":
    try:
        app = MainApp()
        app.run()
    except Exception as e:
        import traceback
        traceback.print_exc()


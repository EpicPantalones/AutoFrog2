from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

import json
import os

STATE_FILE = "state.json"

class PersistentState:
    def __init__(self):
        self.state = {
            "channels": {
                str(i): {
                    "name": f"Channel {i}",
                    "on_time": None,
                    "off_time": None,
                    "current_state": False
                } for i in range(1, 9)
            }
        }
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                self.state = json.load(f)

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=4)

    def set_channel(self, channel, name=None, on_time=None, off_time=None, current_state=None):
        ch = self.state["channels"].get(str(channel))
        if ch is None:
            return
        if name is not None:
            ch["name"] = name
        if on_time is not None:
            ch["on_time"] = on_time
        if off_time is not None:
            ch["off_time"] = off_time
        if current_state is not None:
            ch["current_state"] = current_state
        self.save_state()

    def get_channel(self, channel):
        return self.state["channels"].get(str(channel))

    def get_all_channels(self):
        return self.state["channels"]
    
state = PersistentState()

channels = {
    int(ch): {
        "name": config["name"],
        "state": config["current_state"],
        "on_time": config["on_time"],
        "off_time": config["off_time"]
    }
    for ch, config in state.get_all_channels().items()
}

def control_gpio(channel, state):
    # Placeholder for GPIO control
    print(f"GPIO Control - Channel: {channel}, State: {'ON' if state else 'OFF'}")

def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        state_changed = False
        for ch, config in channels.items():
            if config["on_time"] == now and not config["state"]:
                config["state"] = True
                control_gpio(ch, True)
                state.set_channel(ch, current_state=True)
                state_changed = True
            if config["off_time"] == now and config["state"]:
                config["state"] = False
                control_gpio(ch, False)
                state.set_channel(ch, current_state=False)
                state_changed = True
        if state_changed:
            state.save_state()
        time.sleep(60)

threading.Thread(target=scheduler, daemon=True).start()

@app.route('/')
def index():
    return render_template('index.html', channels=channels)

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    ch = int(data['channel'])
    if 'state' in data:
        channels[ch]['state'] = data['state']
        control_gpio(ch, data['state'])
        state.set_channel(ch, current_state=data['state'])
    if 'name' in data:
        channels[ch]['name'] = data['name']
        state.set_channel(ch, name=data['name'])
    if 'on_time' in data:
        channels[ch]['on_time'] = data['on_time']
        state.set_channel(ch, on_time=data['on_time'])
    if 'off_time' in data:
        channels[ch]['off_time'] = data['off_time']
        state.set_channel(ch, off_time=data['off_time'])
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

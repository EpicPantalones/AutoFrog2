from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from datetime import datetime
import threading
import time
import json
import os
try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    print("RPi.GPIO not available - running in simulation mode")
from password import PASSWORD, SESSION_KEY

app = Flask(__name__)
app.secret_key = SESSION_KEY

STATE_FILE = "state.json"

GPIO_RELAY_MAP = {
    1: 11,
    2: 12,
    3: 13,
    4: 15,
    5: 16,
    6: 18,
    7: 22,
    8: 29,
}

# Initialize GPIO
def init_gpio():
    if GPIO_AVAILABLE:
        GPIO.setmode(GPIO.BOARD)
        for channel, pin in GPIO_RELAY_MAP.items():
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.HIGH)  # Initialize as HIGH (relay off)
        print("GPIO initialized - all relays set to HIGH (OFF)")
    else:
        print("GPIO simulation mode - no actual pins controlled")

class PersistentState:
    def __init__(self):
        self.state = {
            "channels": {
                str(i): {
                    "name": f"Channel {i}",
                    "time_sets": [],
                    "current_state": True
                } for i in range(1, 9)
            }
        }
        self.load_state()

    def load_state(self):
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r") as f:
                try:
                    self.state = json.load(f)
                except json.JSONDecodeError:
                    pass  # fallback to default

    def save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f, indent=4)

    def set_channel(self, channel, name=None, time_sets=None, current_state=None):
        ch = self.state["channels"].get(str(channel))
        if ch is None:
            return
        if name is not None:
            ch["name"] = name
        if time_sets is not None:
            ch["time_sets"] = time_sets
        if current_state is not None:
            ch["current_state"] = current_state
        self.save_state()

    def get_channel(self, channel):
        return self.state["channels"].get(str(channel))

    def get_all_channels(self):
        return self.state["channels"]

state = PersistentState()

def get_runtime_channels():
    return {
        int(ch): {
            "name": config["name"],
            "state": config["current_state"],
            "time_sets": config.get("time_sets", [])
        }
        for ch, config in state.get_all_channels().items()
    }

channels = get_runtime_channels()

def control_gpio(channel, state):
    if GPIO_AVAILABLE:
        pin = GPIO_RELAY_MAP.get(channel)
        if pin:
            # For relays, typically LOW = ON, HIGH = OFF
            GPIO.output(pin, GPIO.LOW if state else GPIO.HIGH)
            channel_name = channels.get(channel, {}).get("name", f"Channel {channel}")
            print(f"GPIO Control: {channel_name} turned {'ON' if state else 'OFF'} (pin {pin})")
        else:
            print(f"Error: No GPIO pin mapped for channel {channel}")
    else:
        channel_name = channels.get(channel, {}).get("name", f"Channel {channel}")
        print(f"GPIO Simulation: {channel_name} would be turned {'ON' if state else 'OFF'} (pin {GPIO_RELAY_MAP.get(channel, 'unknown')})")

def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        state_changed = False
        for ch, config in channels.items():
            for time_pair in config.get("time_sets", []):
                if time_pair.get("on") == now and not config["state"]:
                    config["state"] = True
                    control_gpio(ch, True)
                    state.set_channel(ch, current_state=True)
                    state_changed = True
                elif time_pair.get("off") == now and config["state"]:
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
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    # Your existing index page rendering logic here
    return render_template('index.html', channels=channels)  # Placeholder

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        entered = request.form.get('password', '')
        if entered == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid password')
    return render_template('login.html')

@app.route('/update', methods=['POST'])
def update():
    data = request.get_json()
    ch = int(data['channel'])

    # Apply updates to runtime and persistent state
    if 'state' in data:
        channels[ch]['state'] = data['state']
        control_gpio(ch, data['state'])
    if 'name' in data:
        channels[ch]['name'] = data['name']
    if 'time_sets' in data:
        channels[ch]['time_sets'] = data['time_sets']

    # Save to persistent state
    state.set_channel(
        ch,
        name=channels[ch]['name'],
        time_sets=channels[ch]['time_sets'],
        current_state=channels[ch]['state']
    )

    return jsonify(success=True)

if __name__ == '__main__':
    init_gpio()
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        if GPIO_AVAILABLE:
            GPIO.cleanup()
            print("GPIO cleanup completed")
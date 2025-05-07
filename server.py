from flask import Flask, render_template, request, jsonify
from datetime import datetime
import threading
import time

app = Flask(__name__)

channels = {
    i: {"name": f"Channel {i+1}", "state": False, "on_time": None, "off_time": None}
    for i in range(8)
}

def control_gpio(channel, state):
    # Placeholder for GPIO control
    print(f"GPIO Control - Channel: {channel}, State: {'ON' if state else 'OFF'}")

def scheduler():
    while True:
        now = datetime.now().strftime("%H:%M")
        for ch, config in channels.items():
            if config["on_time"] == now:
                config["state"] = True
                control_gpio(ch, True)
            if config["off_time"] == now:
                config["state"] = False
                control_gpio(ch, False)
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
    if 'name' in data:
        channels[ch]['name'] = data['name']
    if 'on_time' in data:
        channels[ch]['on_time'] = data['on_time']
    if 'off_time' in data:
        channels[ch]['off_time'] = data['off_time']
    return jsonify(success=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# AutoFrog 2.0

## Description

## Setup Instructions (Windows based)

### Ensure SSH is Installed on PowerShell (Windows)

1. Open PowerShell.
2. Check if SSH is available by running:

    ```sh
    ssh
    ```

3. If you see a usage message, SSH is installed. If you get an error, install the OpenSSH Client:
    - Open **Settings** → **Apps** → **Optional Features** → **Add a feature**.
    - Find and install **OpenSSH Client**.
4. Verify installation by running:

    ```sh
    ssh
    ```

### SSH onto the Raspberry Pi (Ethernet Connection)

1. Connect the Raspberry Pi to your computer using an Ethernet cable.
2. Ensure your PC shares internet with the Ethernet device or assign a static IP if necessary.
3. Open PowerShell.
4. Run:

    ```sh
    ssh admin@AutoFrog.local
    ```

5. When prompted, enter the password:

    ```sh
    admin
    ```

> If `.local` hostname resolution fails, use the Pi's IP address instead.

### (Optional) Add Basic Protections

#### Change the Admin password

1. After SSH login, run:

    ```sh
    passwd
    ```

2. Enter the current password (`admin`) when prompted.
3. Enter a new strong password and confirm.

#### Change the default SSH port

1. Edit the SSH configuration file:

    ```sh
    sudo nano /etc/ssh/sshd_config
    ```

2. Find the line:

    ```conf
    #Port 22
    ```

3. Uncomment it by removing the `#` and change `22` to your desired port (e.g., `2222`):

    ```conf
    Port 2222
    ```

4. Save and exit (`Ctrl+O`, `Enter`, then `Ctrl+X`).
5. Restart SSH:

    ```sh
    sudo systemctl restart ssh
    ```

6. Future SSH connections must specify the new port:

    ```sh
    ssh -p 2222 admin@AutoFrog.local
    ```

### Connect the Raspberry Pi to a Wi-Fi Network

1. After SSH login, open the `wpa_supplicant.conf` file:

    ```sh
    sudo nano /etc/wpa_supplicant/wpa_supplicant.conf
    ```

2. Add the following to the end of the file:

    ```conf
    network={
        ssid="YourNetworkName"
        psk="YourNetworkPassword"
    }
    ```

3. Save and exit (`Ctrl+O`, `Enter`, then `Ctrl+X`).
4. Restart networking:

    ```sh
    sudo wpa_cli -i wlan0 reconfigure
    ```

#### Test Wi-Fi Connection

1. Check if the Pi has an IP address on the wireless interface:

    ```sh
    ifconfig
    ```

2. Look for a valid `inet` IP address (e.g., `192.168.x.x`) under an interface named `wlan0` or `wlp2s0`..

3. Ping an external server to verify internet connectivity:

    ```sh
    ping -c 4 google.com
    ```

### Shut Down the Raspberry Pi

1. Run:

    ```sh
    sudo shutdown now
    ```

2. Wait until all lights indicate safe power down before unplugging.

## Interfacing to the Autofrog

Whenever AutoFrog is connected to power and internet, it will automatically boot the webserver, located at `http://<your-pi-ip>:5000/`

### Installation to a Raspberry Pi


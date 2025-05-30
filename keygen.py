import secrets

def generate_flask_secret_key():
    return secrets.token_hex(32)  # 64-character hex string (256 bits)

if __name__ == "__main__":
    print(generate_flask_secret_key())

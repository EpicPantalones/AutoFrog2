import secrets

def generate_flask_secret_key(length: int = 32) -> str:
    return secrets.token_hex(length)

if __name__ == "__main__":
    print("Enter the length of the secret key (default is 32):")
    try:
        user_input = input().strip()
        if user_input.isdigit():
            if int(user_input) < 32:
                print("Key length must be at least 32 characters.")
                key_length = 32
            elif int(user_input) > 128:
                print("Key length must not exceed 128 characters.")
                key_length = 128
            else:
                key_length = int(user_input)
        else:
            print("Invalid input, using default key length of 32 characters.")
            key_length = 32
    except EOFError:
        print("No input provided, using default key length of 32 characters.")
        key_length = 32
    
    print("Enter the new webserver password:")
    user_input_password = input().strip()
    while not user_input_password:
        print("Password cannot be empty. Please enter the new password (default is 'password'):")
        user_input_password = input().strip()

    print("Please confirm the new password:")
    confirm_password = input().strip()

    while confirm_password != user_input_password:
        print("Passwords do not match. Please enter the new password again:")
        user_input_password = input().strip()
        while not user_input_password:
            print("Password cannot be empty. Please enter the new password (default is 'password'):")
            user_input_password = input().strip()
        print("Please confirm the new password:")
        confirm_password = input().strip()

    with open("password.py", "w") as f:
        f.write(f'SESSION_KEY = "{generate_flask_secret_key(key_length)}"\nPASSWORD = "{user_input_password}"\n')
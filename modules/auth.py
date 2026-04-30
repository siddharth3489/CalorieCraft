import json
import re
from pathlib import Path
USERS_FILE = Path(__file__).parent.parent / "data" / "users.json"
def is_valid_username(username):
    if len(username) < 3 or len(username) > 15:
        return False
    
    return re.match(r"^[a-zA-Z0-9_]+$", username) is not None
def is_valid_password(password):
    if len(password) < 6:
        return False
    a = False
    b = False
    for c in password:
        if c.isalpha():
            a = True
        if c.isdigit():
            b = True
    if a == True and b == True:
        return True
    return False
def load_users():
    if USERS_FILE.exists():
        x = USERS_FILE.read_text()
        return json.loads(x)
    return {}
#fetch saved users
def save_users(users):
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(json.dumps(users, indent=2))


#register user
def register(username, password):
    username = username.strip().lower()

    if not is_valid_username(username):
        return False, "Username must be 3-15 letters, digits or underscore."
    if not is_valid_password(password):
        return False, "Password must be 6+ chars with a letter and a digit."
    var1 = load_users()
    if username in var1:
        return False, "Username already exists."
    var1[username] = password
    save_users(var1)
    return True, "Registration successful!"
def login(username, password):
    username = username.strip().lower()
    var1 = load_users()
    if username not in var1:
        return False, "Username not found."
    
    if var1[username] != password:
        return False, "Incorrect password."
    return True, "Login successful!"

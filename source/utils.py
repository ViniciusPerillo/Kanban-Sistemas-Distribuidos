import datetime

def print_log(msg: str = ''):
    print(f"[{datetime.datetime.now()}] {msg}")

def print_warning(msg: str = ''):
    print(f"\033[91m[{datetime.datetime.now()}] {msg}\033[90m")
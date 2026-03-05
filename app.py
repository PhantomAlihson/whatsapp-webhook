from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = "meutoken123"

@app.route("/", methods=["GET"])
def home():
    return "Servidor Railway funcionando!"

@app.route("/webhook", methods=["GET", "POST"])
def webhook():

    # Verificação do webhook da Meta
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        else:
            return "Verification failed", 403

    # Recebendo eventos (mensagens)
    if request.method == "POST":
        data = request.get_json()
        print("Webhook recebido:", data)
        return "EVENT_RECEIVED", 200

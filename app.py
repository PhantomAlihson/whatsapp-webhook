from flask import Flask, request

app = Flask(__name__)

@app.get("/")
def home():
    return "Servidor Railway funcionando!"

@app.post("/webhook")
def webhook():
    data = request.get_json(silent=True)
    print("Webhook recebido:", data)
    return "EVENT_RECEIVED", 200

from flask import Flask, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "Servidor WhatsApp rodando!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Mensagem recebida:", data)
    return "ok"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

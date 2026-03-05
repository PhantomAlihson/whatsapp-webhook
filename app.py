import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID", "")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN", "")
GRAPH_VERSION = os.getenv("GRAPH_VERSION", "v20.0")

@app.get("/")
def home():
    return "Servidor WhatsApp rodando!"

# ✅ Meta usa GET para verificar o webhook
@app.get("/webhook")
def webhook_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403

def send_whatsapp_message(to_number: str, text: str):
    if not PHONE_NUMBER_ID or not WHATSAPP_TOKEN:
        print("Faltam variáveis PHONE_NUMBER_ID ou WHATSAPP_TOKEN no Railway.")
        return

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text}
    }

    r = requests.post(url, headers=headers, json=payload, timeout=20)
    print("Send status:", r.status_code, r.text)

# ✅ Meta manda POST com as mensagens
@app.post("/webhook")
def webhook_receive():
    data = request.get_json(silent=True) or {}
    print("Mensagem recebida:", data)

    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])
        if not messages:
            return "ok", 200

        msg = messages[0]
        from_number = msg.get("from")  # número de quem mandou
        text = (msg.get("text") or {}).get("body", "")

        if from_number and text:
            # Resposta automática (teste)
            send_whatsapp_message(from_number, f"Recebi sua mensagem: {text}")
    except Exception as e:
        print("Erro ao processar webhook:", e)

    return "ok", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

import os
import requests
from flask import Flask, request

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "meutoken123")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
WHATSAPP_TOKEN = os.getenv("WHATSAPP_TOKEN")

GRAPH_VERSION = "v20.0"  # pode funcionar com v19/v20/v21 também


def send_whatsapp_text(to_number: str, text: str) -> None:
    """Envia mensagem de texto pela WhatsApp Cloud API."""
    if not PHONE_NUMBER_ID or not WHATSAPP_TOKEN:
        print("Faltam variáveis PHONE_NUMBER_ID ou WHATSAPP_TOKEN no Railway.")
        return

    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_number,
        "type": "text",
        "text": {"body": text},
    }

    r = requests.post(url, headers=headers, json=payload, timeout=15)
    print("Send status:", r.status_code, r.text)


@app.get("/")
def home():
    return "Servidor Railway funcionando!"


@app.route("/webhook", methods=["GET", "POST"])
def webhook():
    # 1) Verificação do webhook (Meta chama via GET)
    if request.method == "GET":
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == VERIFY_TOKEN:
            return challenge, 200
        return "Forbidden", 403

    # 2) Recebendo mensagens (Meta chama via POST)
    data = request.get_json(silent=True) or {}
    print("Webhook recebido:", data)

    try:
        entry = data.get("entry", [])
        if not entry:
            return "EVENT_RECEIVED", 200

        changes = entry[0].get("changes", [])
        if not changes:
            return "EVENT_RECEIVED", 200

        value = changes[0].get("value", {})
        messages = value.get("messages", [])

        # Se não for evento de mensagem, só confirma
        if not messages:
            return "EVENT_RECEIVED", 200

        msg = messages[0]
        from_number = msg.get("from")  # número do cliente (sem +)
        msg_type = msg.get("type")

        # Texto digitado pelo cliente
        user_text = ""
        if msg_type == "text":
            user_text = msg.get("text", {}).get("body", "").strip()

        # Resposta automática (v1)
        reply = (
            "Olá! 👋 Sou Liz, assistente virtual da A2BNow.\n"
            "Obrigado por entrar em contato 😊\n\n"
            "Me diga: você precisa de *Site*, *Logo* ou *Redes Sociais*?"
        )

        # Se quiser, dá pra customizar com base no que o cliente escreveu:
        if user_text:
            lower = user_text.lower()
            if "site" in lower or "web" in lower:
                reply = (
                    "Perfeito! 🖥️ Vamos falar do seu site.\n"
                    "Você quer um site para *empresa*, *serviço* ou *loja online*?\n"
                    "E qual é o prazo ideal?"
                )
            elif "logo" in lower or "logomarca" in lower:
                reply = (
                    "Perfeito! 🎨 Vamos criar sua logo.\n"
                    "Qual é o nome da sua marca e que estilo você prefere (moderno, minimalista, clássico)?"
                )
            elif "rede" in lower or "instagram" in lower:
                reply = (
                    "Ótimo! 📱 Vamos cuidar das suas redes.\n"
                    "Qual é seu nicho e quantas postagens por semana você deseja?"
                )

        if from_number:
            send_whatsapp_text(from_number, reply)

    except Exception as e:
        print("Erro processando webhook:", str(e))

    return "EVENT_RECEIVED", 200

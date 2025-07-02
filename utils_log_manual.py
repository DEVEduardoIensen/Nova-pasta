# utils_log_manual.py
import json
import os
from datetime import datetime

LOG_FILE = "log_conversa_manual.json"

def carregar_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w") as f:
            json.dump([], f, indent=2)
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def registrar_mensagem(papel, mensagem):
    log = carregar_log()
    log.append({
        "timestamp": datetime.utcnow().isoformat(),
        "quem": papel,
        "mensagem": mensagem
    })
    with open(LOG_FILE, "w") as f:
        json.dump(log, f, indent=2)

def limpar_log():
    with open(LOG_FILE, "w") as f:
        json.dump([], f, indent=2)

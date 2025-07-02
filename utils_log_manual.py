import json
import os

ARQUIVO_LOG = "log_conversa_manual.json"

def carregar_log():
    if not os.path.exists(ARQUIVO_LOG):
        return []

    try:
        with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
            conteudo = f.read().strip()
            if not conteudo:
                return []
            log = json.loads(conteudo)
            if isinstance(log, list):
                return log
            else:
                return []  # Evita erro se for dict ou lixo
    except Exception as e:
        print(f"⚠️ Erro ao carregar log manual: {e}")
        return []

def registrar_mensagem(remetente, mensagem):
    log = carregar_log()
    log.append({
        "remetente": remetente,
        "mensagem": mensagem
    })
    with open(ARQUIVO_LOG, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

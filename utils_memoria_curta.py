import json
import os

ARQUIVO_MEMORIA_CURTA = "memoria_curta_gpt.json"

def carregar_memoria_curta():
    if os.path.exists(ARQUIVO_MEMORIA_CURTA):
        with open(ARQUIVO_MEMORIA_CURTA, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def salvar_memoria_curta(novos_dados):
    dados = carregar_memoria_curta()
    dados.update(novos_dados)
    with open(ARQUIVO_MEMORIA_CURTA, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

def apagar_da_memoria_curta(chaves):
    dados = carregar_memoria_curta()
    for chave in chaves:
        dados.pop(chave, None)
    with open(ARQUIVO_MEMORIA_CURTA, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False)

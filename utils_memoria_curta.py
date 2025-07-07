import json
import os

ARQUIVO_MEMORIA_CURTA = "memoria_curta_gpt.json"

# ✅ Lê o conteúdo atual da memória curta
def carregar_memoria_curta():
    if not os.path.exists(ARQUIVO_MEMORIA_CURTA):
        return {}
    try:
        with open(ARQUIVO_MEMORIA_CURTA, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}  # Arquivo corrompido ou vazio
    except Exception as e:
        print(f"❌ Erro ao carregar memória curta: {e}")
        return {}

# ✅ Salva (ou atualiza) um ou mais itens na memória curta
def salvar_memoria_curta(novos_dados: dict):
    dados = carregar_memoria_curta()
    dados.update(novos_dados)
    try:
        with open(ARQUIVO_MEMORIA_CURTA, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao salvar na memória curta: {e}")

# ✅ Apaga uma ou mais chaves da memória curta
def apagar_da_memoria_curta(chaves: list):
    dados = carregar_memoria_curta()
    for chave in chaves:
        dados.pop(chave, None)
    try:
        with open(ARQUIVO_MEMORIA_CURTA, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao apagar da memória curta: {e}")

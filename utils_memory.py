import json
import os

MEMORY_FILE = "memory_gpt.json"

# ✅ Lê o conteúdo da memória fixa (permanente)
def carregar_memoria():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}
    except Exception as e:
        print(f"❌ Erro ao carregar memória fixa: {e}")
        return {}

# ✅ Salva (ou atualiza) informações permanentes na memória
def salvar_na_memoria(nova_entrada: dict):
    memoria = carregar_memoria()
    memoria.update(nova_entrada)
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(memoria, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"❌ Erro ao salvar na memória fixa: {e}")

# ✅ Apaga toda a memória fixa
def apagar_memoria():
    try:
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)
    except Exception as e:
        print(f"❌ Erro ao apagar a memória fixa: {e}")

# ✅ Busca uma chave por trecho do nome
def buscar_valor(parte_da_chave: str):
    memoria = carregar_memoria()
    for chave in memoria.keys():
        if parte_da_chave.lower() in chave.lower():
            return chave
    return None

# ✅ Exporta a memória em formato de texto (para o prompt do GPT)
def exportar_memoria_texto():
    memoria = carregar_memoria()
    return "\n".join([f"{chave}: {valor}" for chave, valor in memoria.items()])

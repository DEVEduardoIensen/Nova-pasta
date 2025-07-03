# utils_memory.py
import json
import os

MEMORY_FILE = "memory_gpt.json"

def carregar_memoria():
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w") as f:
            json.dump({}, f, indent=2)
    with open(MEMORY_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}

def salvar_na_memoria(nova_entrada):
    memoria = carregar_memoria()
    memoria.update(nova_entrada)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memoria, f, indent=2)

def apagar_memoria():
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f, indent=2)

def buscar_valor(parte_da_chave):
    memoria = carregar_memoria()
    for chave in memoria.keys():
        if parte_da_chave.lower() in chave.lower():
            return chave
    return None

def exportar_memoria_texto():
    memoria = carregar_memoria()
    return "\n".join([f"{chave}: {valor}" for chave, valor in memoria.items()])


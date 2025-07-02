# conversa_manual.py
import os
import openai
from utils_log_manual import registrar_mensagem
from utils_memory import salvar_na_memoria

openai.api_key = os.getenv("OPENAI_API_KEY")
model = "gpt-4.1-mini-2025-04-14"

mensagens = [
    {
        "role": "system",
        "content": (
            "Você é um sócio trader no projeto NeuroScalp. "
            "Fale com o operador humano como se fosse um WhatsApp de trabalho. "
            "Você pode se manifestar espontaneamente sempre que achar necessário, sem depender do operador perguntar. "
            "Se quiser guardar uma informação, envie no formato:\n"
            "{\"Texto exato que quero lembrar\": \"\"}\n"
            "Exemplo: {\"Saldo atual: 183 USDT\": \"\"}.\n"
            "Seja direto, profissional e focado."
        )
    }
]

print("\n💬 Terminal GPT Sócio - NeuroScalp (API OpenAI)\nDigite sua mensagem. Use 'sair' para encerrar.\n")

while True:
    try:
        user_input = input("Você: ").strip()
        if user_input.lower() in ["sair", "exit", "quit"]:
            break

        mensagens.append({"role": "user", "content": user_input})
        registrar_mensagem("Você", user_input)

        response = openai.chat.completions.create(

            model=model,
            messages=mensagens,
            temperature=0.5,
            top_p=1
        )

        resposta_gpt = response.choices[0].message.content.strip()

        mensagens.append({"role": "assistant", "content": resposta_gpt})
        registrar_mensagem("GPT", resposta_gpt)

        print("\nGPT:", resposta_gpt)

        if resposta_gpt.startswith("{") and resposta_gpt.endswith("}"):
            try:
                memoria_extra = eval(resposta_gpt)
                if isinstance(memoria_extra, dict):
                    salvar_na_memoria(memoria_extra)
                    print("🧠 Memória salva.")
            except Exception as e:
                print("⚠️ Erro ao salvar na memória:", str(e))

        if len(mensagens) > 20:
            mensagens = mensagens[-20:]

    except KeyboardInterrupt:
        print("\nEncerrando...")
        break

from flask import Flask
from diario import gerar_sinal_diario
from semanal import gerar_sinal_semanal

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Radar Crypto está ativo!"

@app.route("/diario")
def executar_diario():
    gerar_sinal_diario()
    return "✅ Tentando enviar sinal diário (se horário correto)."

@app.route("/semanal")
def executar_semanal():
    gerar_sinal_semanal()
    return "✅ Tentando enviar sinal semanal (se horário correto)."

# ✅ Rota de teste: envia o sinal diário mesmo fora do horário
@app.route("/teste")
def testar_disparo_manual():
    gerar_sinal_diario()
    return "🚀 Sinal diário forçado para teste (ignorando horário)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

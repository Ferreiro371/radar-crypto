from flask import Flask
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal, enviar_sinal

app = Flask(__name__)

@app.route("/")
def home():
    return "🌐 Radar Crypto está online."

@app.route("/diario")
def diario():
    print("⏰ Rota /diario acionada.")
    gerar_sinal_diario()
    return "✅ Tentando enviar sinal diário (se horário correto)."

@app.route("/semanal")
def semanal():
    print("⏰ Rota /semanal acionada.")
    gerar_sinal_semanal()
    return "✅ Tentando enviar sinal semanal (se horário correto)."

@app.route("/teste")
def teste():
    print("🔧 Rota de teste acessada")
    token = {
        "name": "Ethereum",
        "symbol": "eth",
        "total_volume": 100000000,
        "current_price": 3000.00,
        "price_change_percentage_24h": 4.25,
        "id": "ethereum"
    }
    sentimento = "Positivo ✅"
    expectativa = "+5% a +15% em 1 a 3 dias"
    enviar_sinal(token, sentimento, expectativa, tipo="teste")
    return "✅ Sinal de teste enviado para o Telegram (se tudo estiver correto)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

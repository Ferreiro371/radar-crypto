from flask import Flask
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal, enviar_sinal

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Radar Crypto (modo grátis) online."

@app.route("/diario", methods=["GET", "HEAD"])
def diario():
    gerar_sinal_diario()
    return "✅ Sinal diário: tentativa de envio executada."

@app.route("/semanal", methods=["GET", "HEAD"])
def semanal():
    gerar_sinal_semanal()
    return "✅ Sinal semanal: tentativa de envio executada."

@app.route("/teste", methods=["GET"])
def teste():
    # Sinal de teste estático — só para validar Telegram
    token = {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "btc",
        "current_price": 64000.0,
        "total_volume": 123456789,
        "price_change_percentage_24h": 2.1,
        "market_cap_rank": 1
    }
    sentimento = "Positivo ✅"
    expectativa = "+3% a +8%"
    horizonte = "1–3 dias"
    enviar_sinal(token, sentimento, expectativa, horizonte, tipo="diario")
    return "✅ Sinal de teste enviado (se variáveis de ambiente estiverem corretas)."

if __name__ == "__main__":
    # Render normalmente roda em 8080
    app.run(host="0.0.0.0", port=8080)

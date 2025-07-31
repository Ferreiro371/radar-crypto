from flask import Flask
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ API do Radar está no ar!"

@app.route("/diario", methods=["GET", "HEAD"])
def diario():
    gerar_sinal_diario()
    return "✅ Sinal diário verificado (se horário for compatível, foi enviado ao Telegram)."

@app.route("/semanal", methods=["GET", "HEAD"])
def semanal():
    gerar_sinal_semanal()
    return "✅ Sinal semanal verificado (se horário for compatível, foi enviado ao Telegram)."

@app.route("/teste", methods=["GET"])
def teste():
    token = {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "btc",
        "current_price": 63758,
        "total_volume": 123456789,
        "price_change_percentage_24h": 2.5,
        "market_cap_rank": 1
    }
    sentimento = "Positivo ✅"
    expectativa = "+5% a +15% em 1 a 3 dias"
    from radar_bot import enviar_sinal
    enviar_sinal(token, sentimento, expectativa, tipo="semanal")
    return "✅ Sinal de teste enviado para o Telegram (se tudo estiver correto)."

if __name__ == "__main__":
    app.run(debug=False, port=8080)

from flask import Flask
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Radar Crypto está online."

@app.route("/diario")
def diario():
    gerar_sinal_diario()
    return "✅ Sinal diário enviado."

@app.route("/semanal")
def semanal():
    gerar_sinal_semanal()
    return "✅ Sinal semanal enviado."

@app.route("/teste")
def teste():
    token = {
        "name": "TesteCoin",
        "symbol": "tst",
        "total_volume": 1000000,
        "current_price": 0.1234,
        "price_change_percentage_24h": 5.67,
        "market_cap_rank": 123,
        "id": "bitcoin"
    }
    sentimento = "Positivo ✅"
    expectativa = "+5% a +15% em 1 a 3 dias"
    from radar_bot import enviar_sinal
    enviar_sinal(token, sentimento, expectativa, tipo="teste")
    return "✅ Sinal de teste enviado para o Telegram (se tudo estiver correto)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

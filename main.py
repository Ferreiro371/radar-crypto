from flask import Flask
from radar_bot import get_top_tokens, selecionar_token_diario, analyze_sentiment_api, estimar_valorizacao, enviar_sinal

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Radar está online!"

@app.route("/teste")
def teste():
    posts = ["Amazing dev team", "High volume", "Community talking"]
    tokens = get_top_tokens()
    if not tokens:
        return "❌ Erro ao buscar tokens."
    token = selecionar_token_diario(tokens)
    sentimento = analyze_sentiment_api(posts)
    expectativa = estimar_valorizacao(token, sentimento)
    enviar_sinal(token, sentimento, expectativa, tipo="teste")
    return "✅ Sinal de teste enviado para o Telegram (se tudo estiver correto)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

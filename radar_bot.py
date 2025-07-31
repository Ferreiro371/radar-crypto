import requests
import time
import os
from datetime import datetime

HF_API_URL = "https://api-inference.huggingface.co/models/distilbert/distilbert-base-uncased-finetuned-sst-2-english"
HEADERS = {"Authorization": f"Bearer {os.getenv('HF_API_TOKEN')}"}

def analyze_sentiment_api(posts):
    results = []
    for post in posts:
        try:
            response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": post})
            while response.status_code == 503:
                time.sleep(1)
                response = requests.post(HF_API_URL, headers=HEADERS, json={"inputs": post})
            data = response.json()
            label = data[0][0]["label"] if isinstance(data, list) else "NEUTRAL"
        except Exception:
            label = "NEUTRAL"
        results.append(label)
    pos = results.count("POSITIVE")
    neg = results.count("NEGATIVE")
    if pos > neg:
        return "Positivo ✅"
    elif neg > pos:
        return "Negativo ⚠️"
    else:
        return "Neutro 🤔"

def estimar_valorizacao(token, sentimento):
    volume = token.get("total_volume", 0)
    variacao = token.get("price_change_percentage_24h", 0)
    if sentimento.startswith("Positivo") and variacao > 5 and volume > 1_000_000:
        return "+15% a +30% em 1 semana"
    elif sentimento.startswith("Positivo") and variacao > 1:
        return "+5% a +15% em 1 a 3 dias"
    elif sentimento.startswith("Neutro"):
        return "+0% a +5% em 24h"
    else:
        return "-5% a +5% (volátil nas próximas horas)"

def get_top_tokens(limit=100):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"❌ Erro ao acessar CoinGecko: {e}")
        return []

def selecionar_token_diario(tokens):
    best, best_score = None, -1
    for token in tokens:
        if not isinstance(token, dict): continue
        score = 0
        if token.get("price_change_percentage_24h", 0) > 3:
            score += 1
        if isinstance(token.get("market_cap_rank"), int) and token["market_cap_rank"] < 200:
            score += 1
        if token.get("total_volume", 0) > 500000:
            score += 1
        if score > best_score:
            best, best_score = token, score
    return best

def selecionar_token_semanal(tokens):
    for token in tokens:
        if not isinstance(token, dict): continue
        if (
            token.get("price_change_percentage_24h", 0) > 5 and
            token.get("total_volume", 0) > 5_000_000 and
            isinstance(token.get("market_cap_rank"), int) and token["market_cap_rank"] < 100
        ):
            return token
    return None

def enviar_sinal(token, sentimento, expectativa, tipo="diario"):
    import os
    import requests

    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")

    name = token.get("name")
    symbol = token.get("symbol", "").upper()
    volume = "${:,.0f}".format(token.get("total_volume", 0))
    price = "${:,.4f}".format(token.get("current_price", 0))
    percent = "{:+.2f}%".format(token.get("price_change_percentage_24h", 0))
    tag = "🚨 <b>Sinal Diário</b>" if tipo == "diario" else "💎 <b>Oportunidade da Semana</b>"

    message = (
        f"{tag}\n\n"
        f"🪙 <b>{name} ({symbol})</b>\n"
        f"💵 <b>Preço atual:</b> {price}\n"
        f"📈 <b>Volume 24h:</b> {volume}\n"
        f"📊 <b>Variação 24h:</b> {percent}\n"
        f"🧠 <b>Sentimento social:</b> {sentimento}\n"
        f"📈 <b>Expectativa de valorização:</b> {expectativa}\n\n"
        f"🔗 <b>Links úteis:</b>\n"
        f"📄 <a href='https://www.coingecko.com/en/coins/{token['id']}'>Ver no CoinGecko</a>\n"
        "📊 <a href='https://www.dextools.io/app/en/ether/pair-explorer'>DexTools</a>"
    )

    image_url = "https://dummyimage.com/600x300/000/fff&text=Sinal"

    print("🔧 Enviando sinal para Telegram...")
    print("📬 TOKEN:", TELEGRAM_BOT_TOKEN)
    print("📬 CHAT_ID:", CHAT_ID)
    print("📬 Mensagem:", message)

    try:
        response_photo = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "photo": image_url}
        )
        print("📡 Resposta do envio da imagem:", response_photo.status_code, response_photo.text)
    except Exception as e:
        print("❌ Erro ao enviar imagem:", e)

    try:
        response_message = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={
                "chat_id": CHAT_ID,
                "text": message,
                "parse_mode": "HTML"
            }
        )
        print("📡 Resposta do envio da mensagem:", response_message.status_code, response_message.text)
    except Exception as e:
        print("❌ Erro ao enviar mensagem:", e)

def gerar_sinal_diario():
    tokens = get_top_tokens()
    if not tokens:
        print("❌ Nenhum token retornado da CoinGecko. Abortando envio.")
        return

    token = selecionar_token_diario(tokens) or tokens[0]
    sentimento = analyze_sentiment_api([
        "Huge volume spike! Something is happening with this coin!",
        "Amazing dev team and promising roadmap.",
        "People on Reddit are hyped about this token!",
        "Positive trend and bullish indicators today.",
        "Influencers are starting to talk about it on Twitter."
    ])
    expectativa = estimar_valorizacao(token, sentimento)
    enviar_sinal(token, sentimento, expectativa, tipo="diario")


def gerar_sinal_semanal():
    tokens = get_top_tokens()
    if not tokens:
        print("❌ Nenhum token retornado da CoinGecko. Abortando envio.")
        return

    token = selecionar_token_semanal(tokens)
    if token:
        sentimento = analyze_sentiment_api([
            "Huge volume spike! Something is happening with this coin!",
            "Amazing dev team and promising roadmap.",
            "People on Reddit are hyped about this token!",
            "Positive trend and bullish indicators today.",
            "Influencers are starting to talk about it on Twitter."
        ])
        expectativa = estimar_valorizacao(token, sentimento)
        enviar_sinal(token, sentimento, expectativa, tipo="semanal")
    else:
        print("📉 Nenhum token qualificado para sinal semanal hoje.")

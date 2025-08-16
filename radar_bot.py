import os
import time
import json
from typing import List, Dict, Any, Optional

import requests

# =========================
# Configurações CoinGecko
# =========================
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
USER_AGENT = "RadarCryptoBot/1.1 (+https://github.com/radar-crypto)"
DEFAULT_TIMEOUT = 20  # segundos


def get_top_tokens(limit: int = 100, retries: int = 3, sleep_s: float = 1.0) -> List[Dict[str, Any]]:
    """Busca top moedas por volume na CoinGecko, com backoff simples para evitar 429."""
    params = {
        "vs_currency": "usd",
        "order": "volume_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False,
    }
    headers = {"User-Agent": USER_AGENT}

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(COINGECKO_URL, params=params, headers=headers, timeout=DEFAULT_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list):
                return data
            print(f"❌ Resposta inesperada da CoinGecko: {data}")
            return []
        except requests.HTTPError as e:
            code = getattr(e.response, "status_code", None)
            print(f"❌ Erro HTTP CoinGecko (tentativa {attempt}/{retries}): {e}")
            # Se for 429 (rate limit), aguarda e tenta de novo
            if code == 429 and attempt < retries:
                time.sleep(sleep_s * attempt)  # backoff linear simples
                continue
            return []
        except Exception as e:
            print(f"❌ Erro CoinGecko (tentativa {attempt}/{retries}): {e}")
            if attempt < retries:
                time.sleep(sleep_s * attempt)
                continue
            return []


# =========================
# Seleção de tokens
# =========================
def selecionar_token_diario(tokens: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Seleciona um token ‘ok’ para o sinal diário (regras mais leves)."""
    best, best_score = None, -1
    for t in tokens:
        if not isinstance(t, dict):
            continue
        score = 0
        # Regras simples
        if t.get("price_change_percentage_24h", 0) > 3:
            score += 1
        if isinstance(t.get("market_cap_rank"), int) and t["market_cap_rank"] < 200:
            score += 1
        if t.get("total_volume", 0) > 500_000:
            score += 1
        if score > best_score:
            best, best_score = t, score
    return best


def selecionar_token_semanal(tokens: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Critérios rígidos; pode não encontrar todo dia (isso é esperado)."""
    for t in tokens:
        if not isinstance(t, dict):
            continue
        if (
            t.get("price_change_percentage_24h", 0) > 5 and
            t.get("total_volume", 0) > 5_000_000 and
            isinstance(t.get("market_cap_rank"), int) and t["market_cap_rank"] < 100
        ):
            return t
    return None


# =========================
# “IA” grátis (heurísticas)
# =========================
POS_KEYWORDS = ("amazing", "great", "bull", "up", "moon", "hype", "spike", "volume", "strong", "dev", "partnership")
NEG_KEYWORDS = ("rug", "scam", "down", "dump", "bad", "weak", "fear", "bear", "selloff", "hack")

def _simple_sentiment(posts: List[str], token: Dict[str, Any]) -> str:
    """
    Heurística simples de sentimento:
      - Conta palavras positivas/negativas (case-insensitive)
      - Ajusta pelo price_change_24h
    Retorna: "POSITIVE", "NEGATIVE" ou "NEUTRAL"
    """
    pos, neg = 0, 0
    for p in posts:
        low = p.lower()
        pos += sum(1 for k in POS_KEYWORDS if k in low)
        neg += sum(1 for k in NEG_KEYWORDS if k in low)

    change = token.get("price_change_percentage_24h", 0) or 0
    if change > 4:
        pos += 1
    if change < -4:
        neg += 1

    if pos > neg:
        return "POSITIVE"
    if neg > pos:
        return "NEGATIVE"
    return "NEUTRAL"


def _simple_expectation(token: Dict[str, Any], sentiment: str) -> Dict[str, str]:
    """
    Heurística para expectativa de valorização + horizonte:
      - Considera sentimento + variação + volume
    """
    vol = float(token.get("total_volume", 0) or 0)
    chg = float(token.get("price_change_percentage_24h", 0) or 0)

    if sentiment == "POSITIVE" and chg > 5 and vol > 1_000_000:
        return {"move": "+15% a +30%", "horizon": "1 semana"}
    if sentiment == "POSITIVE" and chg > 1:
        return {"move": "+5% a +12%", "horizon": "1–3 dias"}
    if sentiment == "NEUTRAL":
        return {"move": "+0% a +5%", "horizon": "24h"}
    return {"move": "-5% a +5% (volátil)", "horizon": "próximas horas"}


def analyze_and_expectation(posts: List[str], token: Dict[str, Any]) -> Dict[str, str]:
    """
    Retorna rótulo pt-br + expectativa e horizonte (modo grátis, sem API).
    """
    s = _simple_sentiment(posts, token)
    if s == "POSITIVE":
        sent_pt = "Positivo ✅"
    elif s == "NEGATIVE":
        sent_pt = "Negativo ⚠️"
    else:
        sent_pt = "Neutro 🤔"

    exp = _simple_expectation(token, s)
    return {"sent_pt": sent_pt, "expected_move": exp["move"], "horizon": exp["horizon"]}


# =========================
# Envio para Telegram
# =========================
def _format_msg(token: Dict[str, Any], sentimento_pt: str, expectativa: str, horizonte: str, tag: str) -> str:
    name = token.get("name")
    symbol = token.get("symbol", "").upper()
    volume = "${:,.0f}".format(token.get("total_volume", 0))
    price = "${:,.4f}".format(token.get("current_price", 0))
    percent = "{:+.2f}%".format(token.get("price_change_percentage_24h", 0))
    cg_id = token.get("id", "bitcoin")

    msg = (
        f"{tag}\n\n"
        f"🪙 <b>{name} ({symbol})</b>\n"
        f"💵 <b>Preço atual:</b> {price}\n"
        f"📈 <b>Volume 24h:</b> {volume}\n"
        f"📊 <b>Variação 24h:</b> {percent}\n"
        f"🧠 <b>Sentimento social:</b> {sentimento_pt}\n"
        f"🎯 <b>Expectativa:</b> {expectativa} em {horizonte}\n\n"
        f"🔗 <b>Links úteis:</b>\n"
        f"📄 <a href='https://www.coingecko.com/en/coins/{cg_id}'>Ver no CoinGecko</a>\n"
        "📊 <a href='https://www.dextools.io/app/en/ether/pair-explorer'>DexTools</a>"
    )
    return msg


def enviar_sinal(token: Dict[str, Any], sentimento_pt: str, expectativa: str, horizonte: str, tipo: str = "diario"):
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    if not TELEGRAM_BOT_TOKEN or not CHAT_ID:
        print("❌ TELEGRAM_BOT_TOKEN/CHAT_ID ausentes no ambiente.")
        return

    tag = "🚨 <b>Sinal Diário</b>" if tipo == "diario" else "💎 <b>Oportunidade da Semana</b>"
    message = _format_msg(token, sentimento_pt, expectativa, horizonte, tag)

    image_url = "https://dummyimage.com/600x300/000/fff&text=Radar+Crypto"

    print("🔧 Enviando ao Telegram...")
    try:
        r1 = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
            data={"chat_id": CHAT_ID, "photo": image_url},
            timeout=DEFAULT_TIMEOUT
        )
        print("📷 sendPhoto:", r1.status_code, r1.text)
    except Exception as e:
        print("❌ Erro sendPhoto:", e)

    try:
        r2 = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            data={"chat_id": CHAT_ID, "text": message, "parse_mode": "HTML"},
            timeout=DEFAULT_TIMEOUT
        )
        print("💬 sendMessage:", r2.status_code, r2.text)
    except Exception as e:
        print("❌ Erro sendMessage:", e)


# =========================
# Entradas principais (cron chama via GET; sem checar horário)
# =========================
def gerar_sinal_base(tipo: str):
    tokens = get_top_tokens()
    if not tokens:
        print("❌ Nenhum token retornado da CoinGecko. Abortando envio.")
        return

    if tipo == "diario":
        token = selecionar_token_diario(tokens) or tokens[0]
    else:
        token = selecionar_token_semanal(tokens)
        if not token:
            print("📉 Nenhum token qualificado para sinal semanal hoje.")
            return

    posts = [
        "Huge volume spike! Something is happening with this coin!",
        "Amazing dev team and promising roadmap.",
        "People on Reddit are hyped about this token!",
        "Positive trend and bullish indicators today.",
        "Influencers are starting to talk about it on Twitter."
    ]
    result = analyze_and_expectation(posts, token)
    enviar_sinal(token, result["sent_pt"], result["expected_move"], result["horizon"], tipo=tipo)


def gerar_sinal_diario():
    gerar_sinal_base("diario")


def gerar_sinal_semanal():
    gerar_sinal_base("semanal")


from radar_bot import get_top_tokens, selecionar_token_diario, analyze_sentiment_api, estimar_valorizacao, enviar_sinal

print("🚀 Iniciando teste de envio de sinal diário (sem restrição de horário)...")

tokens = get_top_tokens()
if not tokens:
    print("❌ Nenhum token obtido. Abortando.")
else:
    token = selecionar_token_diario(tokens) or tokens[0]
    sentimento = analyze_sentiment_api([
        "This coin is going to the moon!",
        "Big spike in volume.",
        "Trending on Twitter and Reddit.",
    ])
    expectativa = estimar_valorizacao(token, sentimento)
    enviar_sinal(token, sentimento, expectativa, tipo="diario")

    print("✅ Sinal diário enviado com sucesso (modo teste).")

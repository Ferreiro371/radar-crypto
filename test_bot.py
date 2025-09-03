#!/usr/bin/env python3
"""
Script para testar o bot localmente
"""
from dotenv import load_dotenv
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal, enviar_sinal
import os

# Carregar variáveis do .env
load_dotenv()

def teste_envio_simples():
    """Teste básico de envio"""
    print("🧪 Testando envio simples...")
    
    # Token de teste
    token_teste = {
        "id": "bitcoin",
        "name": "Bitcoin",
        "symbol": "btc", 
        "current_price": 64000.0,
        "total_volume": 123456789,
        "price_change_percentage_24h": 2.1,
        "market_cap_rank": 1
    }
    
    # Verificar se as variáveis estão carregadas
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("CHAT_ID")
    
    print(f"📋 Bot Token: {'✅ Configurado' if bot_token else '❌ Não encontrado'}")
    print(f"📋 Chat ID: {'✅ Configurado' if chat_id else '❌ Não encontrado'}")
    
    if bot_token and chat_id:
        enviar_sinal(token_teste, "Positivo ✅", "+3% a +8%", "1–3 dias", tipo="diario")
        print("✅ Teste de envio executado!")
    else:
        print("❌ Variáveis de ambiente não configuradas!")

def teste_sinal_diario():
    """Teste completo do sinal diário"""
    print("🧪 Testando sinal diário completo...")
    gerar_sinal_diario()

def teste_sinal_semanal():
    """Teste completo do sinal semanal"""
    print("🧪 Testando sinal semanal completo...")
    gerar_sinal_semanal()

if __name__ == "__main__":
    print("🚀 Iniciando testes do Radar Crypto Bot")
    print("=" * 50)
    
    # Escolha o teste que quer executar:
    print("1. Teste simples de envio")
    print("2. Teste sinal diário completo")
    print("3. Teste sinal semanal completo")
    
    escolha = input("\nEscolha uma opção (1-3): ").strip()
    
    if escolha == "1":
        teste_envio_simples()
    elif escolha == "2":
        teste_sinal_diario()
    elif escolha == "3":
        teste_sinal_semanal()
    else:
        print("Executando teste simples por padrão...")
        teste_envio_simples()

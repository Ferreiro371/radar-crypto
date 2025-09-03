#!/usr/bin/env python3
"""
Script para executar o sinal semanal via cronjob no Render.
Este script será executado semanalmente.
"""

from radar_bot import gerar_sinal_semanal
import sys

def main():
    try:
        print("🚀 Iniciando execução do sinal semanal...")
        gerar_sinal_semanal()
        print("✅ Sinal semanal executado com sucesso!")
        return 0
    except Exception as e:
        print(f"❌ Erro ao executar sinal semanal: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

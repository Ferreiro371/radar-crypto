#!/usr/bin/env python3
"""
Script para executar o sinal diário via cronjob no Render.
Este script será executado diariamente às 22:55.
"""

from radar_bot import gerar_sinal_diario
import sys

def main():
    try:
        print("🚀 Iniciando execução do sinal diário...")
        gerar_sinal_diario()
        print("✅ Sinal diário executado com sucesso!")
        return 0
    except Exception as e:
        print(f"❌ Erro ao executar sinal diário: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

from flask import Flask
from radar_bot import gerar_sinal_diario, gerar_sinal_semanal, enviar_sinal
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit
import logging

app = Flask(__name__)

# Configurar logging para o scheduler
logging.basicConfig(level=logging.INFO)

def job_diario():
    """Job executado diariamente às 22:55"""
    try:
        print("🚀 Executando sinal diário via scheduler...")
        gerar_sinal_diario()
        print("✅ Sinal diário executado com sucesso!")
    except Exception as e:
        print(f"❌ Erro no job diário: {e}")

# Configurar o scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=job_diario,
    trigger=CronTrigger(hour=22, minute=55),  # 22:55 todos os dias
    id='sinal_diario',
    name='Sinal Diário Crypto',
    replace_existing=True
)

# Iniciar o scheduler
scheduler.start()

# Garantir que o scheduler seja finalizado quando a app for fechada
atexit.register(lambda: scheduler.shutdown())

@app.route("/")
def home():
    return "✅ Radar Crypto (modo grátis) online com scheduler automático."

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

@app.route("/status")
def status():
    """Endpoint para verificar o status do scheduler"""
    jobs = []
    for job in scheduler.get_jobs():
        jobs.append({
            'id': job.id,
            'name': job.name,
            'next_run': str(job.next_run_time) if job.next_run_time else 'None'
        })
    return {
        'scheduler_running': scheduler.running,
        'jobs': jobs
    }

if __name__ == "__main__":
    # Render normalmente roda em 8080
    app.run(host="0.0.0.0", port=8080)

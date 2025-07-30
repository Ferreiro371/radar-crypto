
from flask import Flask
import subprocess

app = Flask(__name__)

@app.route("/diario")
def executar_diario():
    subprocess.Popen(["python3", "diario.py"])
    return "✅ Tentando enviar sinal diário (se horário correto)."

@app.route("/semanal")
def executar_semanal():
    subprocess.Popen(["python3", "semanal.py"])
    return "✅ Tentando enviar sinal semanal (se horário correto)."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)

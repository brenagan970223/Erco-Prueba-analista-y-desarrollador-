import os
import sys
import time
import subprocess
import requests
import json

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_title(title):
    print("\n" + "="*70)
    print(f" 🚀 {title}")
    print("="*70 + "\n")

def wait_for_enter(msg="Presiona ENTER para continuar a la siguiente fase..."):
    input(f"\n👉 {msg}")
    print("-" * 50)

def demo_interactivo():
    clear_console()
    print_title("PRESENTACIÓN TÉCNICA: MOTOR ERCO AGPE (Modo Automático)")
    print("Este script interactivo orquestará toda la prueba técnica frente a los evaluadores.")
    wait_for_enter("Dale ENTER para ejecutar el ETL y armar la BD desde Cero...")
    
    # ------------------ PASO 1 ------------------
    print_title("PASO 1: Ingesta ETL en vivo")
    subprocess.run([sys.executable, "etl.py"])
    print("\n✅ Base de datos reconstruida y cruzada.")
    wait_for_enter("ENTER para Validar la Integridad Referencial de los datos...")

    # ------------------ PASO 2 ------------------
    print_title("PASO 2: Validando Relaciones y Keys de Base de Datos")
    subprocess.run([sys.executable, "validate_db.py"])
    wait_for_enter("ENTER para encender el Servidor API FastAPI...")

    # ------------------ PASO 3 ------------------
    print_title("PASO 3: Levantando Servidor Local ASGI (Uvicorn)")
    server = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000", "--host", "127.0.0.1"])
    time.sleep(3) # Tiempo al server para prenderse
    print("\n✅ API online en http://127.0.0.1:8000 y protegida por .env")
    
    headers = {"x-api-key": "agpe_erco_secret_key_12345"}
    
    wait_for_enter("ENTER para disparar una petición POST simulando facturación (Usuario 2256)...")

    # ------------------ PASO 4 ------------------
    print_title("PASO 4: Test Transaccional (Cálculo Fuerte con Pandas)")
    try:
        res1 = requests.post("http://127.0.0.1:8000/calculate-invoice", json={"service_id": 2256}, headers=headers)
        print("Factura Generada:")
        print(json.dumps(res1.json(), indent=2))
    except Exception as e:
        print(f"Error HTTP: {e}")
        
    wait_for_enter("ENTER para disparar los Endpoints Analíticos y Modulares (Usuarios 3222 y 2478)...")

    # ------------------ PASO 5 ------------------
    print_title("PASO 5: Exploración Desacoplada y Analítica")
    try:
        # Analitica Pura
        print("\n>> Consultando Carga General del sistema... (/system-load)")
        res2 = requests.get("http://127.0.0.1:8000/system-load", headers=headers)
        print(json.dumps({"status": res2.json()["status"], "data_len": len(res2.json()["data"])}, indent=2))
        
        # Modular EE2 
        print("\n>> Consultando Solo EE2 usuario 2478... (/calculate-concept)")
        res3 = requests.get("http://127.0.0.1:8000/calculate-concept/2478?concept=EE2", headers=headers)
        print(json.dumps(res3.json(), indent=2))
        
    except Exception as e:
        print(f"Error HTTP: {e}")

    # ------------------ FIN ------------------
    print_title("FIN DE LA DEMOSTRACIÓN")
    print("Apagando servidores en background y limpiando ram.")
    server.kill()
    print("✅ Prueba Técnica terminada. ¡Gracias!")

if __name__ == "__main__":
    demo_interactivo()

import subprocess
import time
import requests
import json

def run_tests():
    print(">>> Levantando el servidor de la API en segundo plano...")
    import sys
    server_process = subprocess.Popen([sys.executable, "-m", "uvicorn", "main:app", "--port", "8000", "--host", "127.0.0.1"])
    time.sleep(4) # Esperar a que el servidor inicialice
    
    headers = {"x-api-key": "agpe_erco_secret_key_12345"}
    
    try:
        print("\n--- PRUEBA 1: Factura Completa Usuario 2256 (Superavitario) ---")
        res1 = requests.post("http://127.0.0.1:8000/calculate-invoice", json={"service_id": 2256}, headers=headers)
        print(json.dumps(res1.json(), indent=2))
        
        print("\n--- PRUEBA 2: Concepto Independiente (EE2) Usuario 2478 ---")
        res2 = requests.get("http://127.0.0.1:8000/calculate-concept/2478?concept=EE2", headers=headers)
        print(json.dumps(res2.json(), indent=2))
        
        print("\n--- PRUEBA 3: Estadísticas Analíticas Usuario 3222 (Industrial) ---")
        res3 = requests.get("http://127.0.0.1:8000/client-statistics/3222", headers=headers)
        print(json.dumps(res3.json(), indent=2))
        
        print("\n--- PRUEBA 4: Concepto Independiente (EA) Usuario 3222 ---")
        res4 = requests.get("http://127.0.0.1:8000/calculate-concept/3222?concept=EA", headers=headers)
        print(json.dumps(res4.json(), indent=2))
        
        print("\n--- PRUEBA 5: Carga Consolidada de la Red (Primeras 2 horas) ---")
        res5 = requests.get("http://127.0.0.1:8000/system-load", headers=headers)
        data_res = res5.json()
        print(json.dumps({"status": data_res["status"], "data_preview": data_res["data"][:2]}, indent=2))
        
    except Exception as e:
        print(f"Error durante las pruebas: {e}")
    finally:
        print("\n>>> Apagando el servidor local...")
        server_process.kill()

if __name__ == "__main__":
    run_tests()

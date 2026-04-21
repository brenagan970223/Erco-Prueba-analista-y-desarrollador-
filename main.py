from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import billing_engine

# Cargar variables de entorno desde el archivo .env
load_dotenv()
API_KEY_LOCAL = os.getenv("API_KEY")

app = FastAPI(
    title="Sistema de Liquidación AGPE - FastAPI",
    description="API RESTful para la facturación de Autogeneradores a Pequeña Escala",
    version="1.0.0"
)

# --- MIDDLEWARE DE SEGURIDAD BÁSICO ---
def verify_api_key(x_api_key: str = Header(None)):
    """Verifica que el usuario mande el API_KEY correcto por el header."""
    if x_api_key != API_KEY_LOCAL:
        raise HTTPException(status_code=401, detail="API Key inválida o no proporcionada en el header 'x-api-key'")

# Esquema para el body del POST Request
class InvoiceRequest(BaseModel):
    service_id: int
    month: str = "2023-09" # Valor por defecto acorde a los datos de la evaluación

# 1. POST /calculate-invoice 
@app.post("/calculate-invoice", tags=["Facturación"], dependencies=[Depends(verify_api_key)])
def calculate_invoice_endpoint(req: InvoiceRequest):
    """
    Calcula la factura completa (EA, EC, EE1, EE2) para un cliente.
    """
    try:
        resultado = billing_engine.calculate_invoice(req.service_id)
        # Inyectamos el mes para dar contexto completo
        resultado["month"] = req.month
        return resultado
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. GET /client-statistics/{service_id}
@app.get("/client-statistics/{service_id}", tags=["Analítica"], dependencies=[Depends(verify_api_key)])
def client_statistics(service_id: int):
    """
    Proporciona estadísticas en crudo de consumo e inyección para un servicio específico
    (Picos horarios, promedios, entre otros).
    """
    try:
        stats = billing_engine.get_client_statistics(service_id)
        return stats
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

# 3. GET /system-load
@app.get("/system-load", tags=["Analítica del Sistema"], dependencies=[Depends(verify_api_key)])
def system_load():
    """
    Muestra la carga energética consolidada de todo el sistema por hora, 
    basada en la data de consumo de todos los usuarios agrupados.
    """
    try:
        carga = billing_engine.get_system_load()
        return {"status": "success", "data": carga}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4. GET (Adicional) Endpoint para el cálculo independiente de cada concepto
@app.get("/calculate-concept/{service_id}", tags=["Facturación Modular"], dependencies=[Depends(verify_api_key)])
def calculate_independent_concept(service_id: int, concept: str):
    """
    Endpoint granular y modular. Permite solicitar Matemáticamente un ÚNICO concepto de facturación.
    Parámetros válidos para el concepto: EA, EC, EE1, EE2.
    """
    if concept.upper() not in ["EA", "EC", "EE1", "EE2"]:
        raise HTTPException(status_code=400, detail="Concepto inválido. Valores permitidos: EA, EC, EE1, EE2.")
        
    try:
        val = billing_engine.calculate_single_concept(service_id, concept)
        return {
            "service_id": service_id, 
            "concept_requested": concept.upper(), 
            "monetary_value_COP": val
        }
    except ValueError as val_err:
        raise HTTPException(status_code=404, detail=str(val_err))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Para correr servidor de prueba: uvicorn main:app --reload

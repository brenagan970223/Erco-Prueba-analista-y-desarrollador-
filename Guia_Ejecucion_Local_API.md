# 🚀 Guía de Ejecución Local y Uso de la API (Sistema AGPE)

Este documento te explica exactamente cómo "prender" tu servidor API en tu propia computadora sin depender de internet y cómo hacer consultas a ella a través de la terminal, tal cual se usaría en producción.

---

## 1. Requisitos Previos e Instalación
Antes de prender la API, asegúrate de tener instaladas las librerías necesarias. Abre una terminal en tu carpeta del proyecto (en Cursor) y ejecuta:
```bash
pip install fastapi uvicorn pandas sqlalchemy python-dotenv
```

---

## 2. Archivo `.env` (Variables de Entorno)
El proyecto cuenta con un archivo oculto llamado `.env` que acabamos de crear en la raíz. Este archivo guarda secretos sin exponerlos en el código.
Actualmente contiene:
```text
API_KEY=agpe_erco_secret_key_12345
DB_PATH=facturacion.db
ENVIRONMENT=local
```
*(Nota: Por simplicidad actual de la prueba el API Key es formativo, y está listo para ser exigido en los headers si se desea mayor seguridad)*

---

## 3. ¿Cómo encender el Servidor API?
Para levantar la API localmente, ejecuta este único comando en tu terminal (asegúrate de estar en la carpeta donde está `main.py`):

```bash
uvicorn main:app --reload
```

**Si todo sale bien, la terminal mostrará esto:**
`Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)`

Con esto, nuestra base de datos simulada y nuestros cálculos con Pandas estarán "vivos" y esperando peticiones por consola.

---

## 4. Swagger UI Automático (La forma Fácil y Gráfica)
FastAPI crea una plataforma visual para ti. Abre tu navegador de Google Chrome y ve a:
👉 **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)**
Allí verás botones para probar tus endpoints con un solo clic.

---

## 5. Pruebas por Consola (CURL) 💻
Si quieres comportarte como un sistema externo simulando peticiones por consola local (como se comunicaría el Front-end), abre **otra** terminal mientras la primera mantiene el servidor prendido, y pega lo siguiente.

### A. Endpoint OBLIGATORIO 1: Calcular la Factura Total (POST)
```bash
curl -X POST "http://127.0.0.1:8000/calculate-invoice" -H "x-api-key: agpe_erco_secret_key_12345" -H "Content-Type: application/json" -d "{\"service_id\": 2256}"
```
**Respuesta Esperada:** JSON completo con EA, EC, EE1, EE2 y totales de Inyección.

### B. Endpoint OBLIGATORIO 2: Estadísticas del Cliente (GET)
```bash
curl -X GET "http://127.0.0.1:8000/client-statistics/2256" -H "x-api-key: agpe_erco_secret_key_12345"
```
**Respuesta Esperada:** JSON con sus picos máximos y promedios horarios.

### C. Endpoint OBLIGATORIO 3: Carga Horaria de la Red (GET)
```bash
curl -X GET "http://127.0.0.1:8000/system-load" -H "x-api-key: agpe_erco_secret_key_12345"
```
**Respuesta Esperada:** Un bloque de JSON denso mostrando, para cada hora del mes de septiembre, cuántos kilovatios totales demandó la red.

### D. Endpoint OBLIGATORIO 4: Cálculo Independiente Modular (GET)
Si solo quieres saber la cantidad de EE2 para el usuario generador 2256:
```bash
curl -X GET "http://127.0.0.1:8000/calculate-concept/2256?concept=EE2" -H "x-api-key: agpe_erco_secret_key_12345"
```
Si requieres saber la Energía Activa:
```bash
curl -X GET "http://127.0.0.1:8000/calculate-concept/2256?concept=EA" -H "x-api-key: agpe_erco_secret_key_12345"
```

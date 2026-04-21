# 🎤 Guion de Sustentación (Prueba Técnica AGPE)

Este documento es tu libreto personal. Cuando te reúnas con los ingenieros o evaluadores de la empresa y compartas pantalla, puedes impresionar ejecutando todo tú mismo siguiendo este guion paso a paso.

---

### ACTO 1: Reconstrucción desde Cero (ETL y Base de datos)
* **🗣️ Lo que vas a decir:** *"Empecemos borrando y cargando toda la base de datos de los CSV crudos desde ceros para que vean el ETL funcionando en vivo"*
* **💻 Lo que vas a teclear en consola:**
  ```bash
  python etl.py
  ```
  *(La terminal mostrará los porcentajes y cómo las tablas se cruzan y se llenan en instantes)*

### ACTO 2: Validación de la Información
* **🗣️ Lo que vas a decir:** *"Ahora, voy a correr mi validador de datos para que miremos cómo las llaves de ForeignKey quedaron perfectas, y cuántos registros quedaron en el sistema."*
* **💻 Lo que vas a teclear:**
  ```bash
  python validate_db.py
  ```
  *(La consola mostrará el conteo y la integridad de la base de datos `facturacion.db`)*

### ACTO 3: Cálculos Nativos Matemáticos y Encendido de API
* **🗣️ Lo que vas a decir:** *"Bien, la lógica nativa ya extrajo todo a los DataFusion. Ahora, voy a prender el servidor de la API para que interactuemos como lo haría un Front-end."*
* **💻 Lo que vas a teclear:**
  ```bash
  uvicorn main:app --reload
  ```
  *(La terminal dirá que la App está viva en el puerto 8000)*

### ACTO 4: Probando el API Seguro
* **🗣️ Lo que vas a decir:** *"El API es seguro y modular. Voy a abrir otra terminal y vamos a pedir la factura completa de un Inyector tipo 1. Noten que debo usar mi llave secreta en la API."*
* **💻 Lo que vas a teclear en una terminal 2:**
  ```bash
  curl -X POST "http://127.0.0.1:8000/calculate-invoice" -H "x-api-key: agpe_erco_secret_key_12345" -H "Content-Type: application/json" -d "{\"service_id\": 2256}"
  ```
  *(La consola escupirá el JSON en milisegundos con los $225.000 de Excedente Tipo 2 del cliente calculados maravillosamente)* 

### ACTO 5: Cierre con Arquitectura Modular
* **🗣️ Lo que vas a decir:** *"Como diseñé esto usando principios modulares, si el Front-end solo necesita imprimir la Energía Activa (EA) y nada más, no tenemos por qué calcular toda la factura. Llamamos al endpoint modular adicional así:"*
* **💻 Lo que vas a teclear:**
  ```bash
  curl -X GET "http://127.0.0.1:8000/calculate-concept/3222?concept=EA" -H "x-api-key: agpe_erco_secret_key_12345"
  ```
  *(La consola escupirá el valor millonario y cerramos la sesión)*.

# Documentación del Sistema de Liquidación AGPE

---

## 📁 ESTRUCTURA DEL REPOSITORIO (ARCHIVOS Y SU USO)
Para que el evaluador comprenda cada pieza antes de ejecutarlo, así está distribuida nuestra solución AGPE:

* **Archivos Python (Lógica Core)**
  * `models.py`: Abstracción ORM (SQLAlchemy). Define el esquema matemático y las relaciones de las tablas antes de crearlas.
  * `etl.py`: Motor pipeline de ingesta de datos. Toma los datos crudos, los transforma y los escribe masivamente en SQLite.
  * `validate_db.py`: Script de aseguramiento de calidad (QA). Valida claves foráneas, huérfanos y límites matemáticos de la DB.
  * `billing_engine.py`: Motor de cálculo optimizado en `Pandas`. Resuelve analíticamente los conceptos EA, EC, EE1 y EE2.
  * `main.py`: Entrada del servidor Backend (FastAPI). Expone de manera segura la infraestructura hacia la Web mediante `x-api-key`.

* **Archivos de Documentación y Setup**
  * `README.md`: Este documento maestro que compila todas las decisiones técnicas del proyecto.
  * `esquema_base_datos.json`: Diccionario de datos en JSON exportable para visualizadores de bases de datos relacionales.
  * `Guia_Ejecucion_Local_API.md`: Manual con snippets CURL para el equipo de Front-end sobre cómo consumir nuestro Backend.
  * `Guion_Sustentacion_Demo.md`: Libreto estratégico pensado para la presentación presencial técnica.
  * `demo_interactivo.py` y `test_api.py`: Scripts preconfigurados para demostraciones de estrés automático del sistema.

* **Archivos Ignorados por seguridad (`.gitignore`)**
  * `.env`: Guarda credenciales secretas y jamás de sube a nube pública.
  * `facturacion.db`: La base de datos es ignorada ya que la instrucción real es que cada quien la regenere en su RAM local corriendo `etl.py`.
  * `*.csv`: (Excepto si la prueba exija publicarlos).

---

## 📁 ARCHIVOS DEL PROYECTO - EXPLICACIÓN DETALLADA

### 1. **models.py** — Definición de Estructura de Base de Datos

**¿Qué es?**
Archivo Python que define la estructura completa de la base de datos usando SQLAlchemy ORM.

**¿Para qué sirve?**
- Define las 6 tablas (entidades) del sistema
- Especifica tipos de datos, claves primarias (PK) y foráneas (FK)
- Establece relaciones entre tablas
- Genera automáticamente la base de datos SQLite

**¿Qué contiene?**
```
✓ Importaciones: sqlalchemy, datetime
✓ Clase Base: declarative_base() - herencia común para todas las tablas
✓ 6 Clases (1 por tabla):
  - class Tariff(Base) — Maestro de tarifas (105 registros)
  - class Service(Base) — Puntos de servicio (3 clientes)
  - class Record(Base) — Registros horarios (2160 mediciones)
  - class Consumption(Base) — Consumo de energía
  - class Injection(Base) — Inyección de energía
  - class XmData(Base) — Precios de bolsa horarios (720 precios)
✓ Función init_db() — Crea facturacion.db con todas las tablas
✓ Documentación: Docstrings en cada clase explicando propósito y relaciones
```

**¿Cómo se usa?**
```python
# Paso 1: Importar en otros archivos
from models import init_db, Tariff, Service, Record, Consumption, Injection, XmData

# Paso 2: Crear la BD
engine = init_db('facturacion.db')

# Paso 3: Usar las clases con SQLAlchemy Session
Session = sessionmaker(bind=engine)
session = Session()
tariff = session.query(Tariff).filter(Tariff.id_market == 1).first()
```

**Ejecución Manual:**
```bash
python models.py
# Salida: ✓ Base de datos inicializada en facturacion.db
```

---

### 2. **etl.py** — Extracción, Transformación y Carga (ETL)

**¿Qué es?**
Script que lee datos de CSVs y los carga en la base de datos.

**¿Para qué sirve?**
- Leer datos de 6 archivos CSV
- Limpiar y parsear tipos de datos (int, float, datetime)
- Insertar en la BD respetando orden de dependencias (FK válidas)
- Validar integridad durante la carga

**¿Qué contiene?**
```
✓ Funciones parse_*(): Leen CSVs y convierten tipos
  - parse_tariffs() — Lee tariffs 4.csv (105 registros)
  - parse_services() — Lee services 4.csv (3 registros)
  - parse_records() — Lee records 4.csv (2160 registros)
  - parse_consumption() — Lee consumption 4.csv (2160 registros)
  - parse_injection() — Lee injection 4.csv (2160 registros)
  - parse_xm_data() — Lee xm_data_hourly_per_agent 4.csv (720 registros)

✓ Funciones load_*(): Insertan en BD en orden correcto
  - load_tariffs() → load_services() → load_records() → load_consumption/injection → load_xm_data()

✓ Función main(): Orquesta todo el proceso con output visual
```

**¿Cómo se usa?**
```bash
python etl.py
# Salida: 
# ============================================================
# INICIANDO ETL - Sistema de Liquidación AGPE
# ============================================================
# [1/8] Inicializando base de datos...
# ... (progreso detallado)
# ✓ ETL COMPLETADO EXITOSAMENTE
```

**Orden de Carga Garantizado:**
1. tariffs (sin dependencias)
2. services (FK → tariffs)
3. records (FK → services)
4. consumption (FK → records)
5. injection (FK → records)
6. xm_data (sin dependencias)

---

### 3. **validate_db.py** — Validación de Integridad de Datos

**¿Qué es?**
Script que verifica que todos los datos se cargaron correctamente y que las relaciones son válidas.

**¿Para qué sirve?**
- Confirmar que no hay registros huérfanos (FK quebradas)
- Verificar cobertura de datos (100% en consumption/injection)
- Mostrar estadísticas descriptivas
- Identificar anomalías o datos faltantes

**¿Qué contiene?**
```
✓ Función validate_db(): 8 pruebas independientes

[1] Validar Tariffs:
    - Contar total de registros
    - Verificar que PK es única (no hay duplicados)
    - Confirmar que cdi es NULL para voltage_level 2/3

[2] Validar Services:
    - Contar total
    - Detectar huérfanos (services sin tariff)
    - Mostrar cada servicio con su mercado y nivel

[3] Validar Records:
    - Contar total (esperado: 2160)
    - Detectar huérfanos (records sin service)
    - Verificar rango temporal

[4] Validar Consumption:
    - Cobertura (2160/2160 = 100%)
    - Detectar huérfanos
    - Estadísticas: Min, Promedio, Max

[5] Validar Injection:
    - Cobertura (2160/2160 = 100%)
    - Detectar huérfanos
    - Estadísticas + contar registros con inyección > 0

[6] Validar XM Data:
    - Contar precios (720)
    - Estadísticas de precios COP/kWh

[7] Validar Cobertura Temporal:
    - Rango en records (2023-09-01 a 2023-09-30)
    - Rango en xm_data (debe ser igual)

[8] Resumen por Servicio:
    - Records por servicio
    - Consumo total acumulado (kWh)
    - Inyección total acumulada (kWh)
```

**¿Cómo se usa?**
```bash
python validate_db.py
# Salida:
# ============================================================
# VALIDACIÓN DE INTEGRIDAD - Sistema de Liquidación AGPE
# ============================================================
# [1] Validando Tariffs...
#   ✓ Total tariffs: 105
#   ✓ Combinaciones únicas: 105
#   ✓ Tariffs nivel 2/3 con cdi no-NULL: 0
# ... (8 pruebas completas)
# ✓ VALIDACIÓN COMPLETADA EXITOSAMENTE
```

**Resultados Obtenidos:**
- ✓ 0 registros huérfanos (integridad perfecta)
- ✓ 100% cobertura en consumption e injection
- ✓ 720 precios XM para toda la serie temporal
- ✓ 3 servicios con datos completos (720 registros c/u)

---

## Flujo de Ejecución Recomendado

```
1. models.py ──→ Crea estructura BD (facturacion.db)
                ↓
2. etl.py     ──→ Carga datos desde CSVs
                ↓
3. validate_db.py → Verifica integridad y estadísticas
                ↓
4. (Próximo) billing_engine.py → Calcula EA, EC, EE1, EE2
```

---

## Paso 1: Análisis de Requisitos y Lógica de Negocio ✓ (Completado)

### Justificación Técnica
- **Revisión del README**: Analizado README V2_ Especificaciones Técnicas y Diseño de DB - Sistema AGPE.txt para entender el esquema relacional normalizado y la lógica regulatoria CREG/AGPE.
- **Análisis de CSVs**: Revisados todos los CSVs (tariffs, services, records, consumption, injection, xm_data_hourly_per_agent) confirmando formatos de datos:
  - Integers: id_market, id_service, voltage_level, cdi, id_record
  - Floats: Componentes tarifarios (G, T, D, R, C, P, CU) con 8 decimales; consumo/inyección con 3 decimales; precios XM con 10 decimales
  - Timestamps: Formato ISO '2023-09-01 00:00:00.000000' (consistente en records y xm_data)
  - Campos anulables: cdi en tariffs para voltage_level 2/3

### Definiciones de Conceptos de Liquidación (Confirmadas)
1. **EA (Energía Activa)**: 
   - Cantidad: Sumatoria de consumption.value (por servicio y mes)
   - Tarifa: CU de tariffs (Costo Unitario)
   - Fórmula: EA = Σ(consumption) × CU

2. **EC (Comercialización de Excedentes)**:
   - Cantidad: Sumatoria de injection.value (por servicio y mes)
   - Tarifa: C de tariffs (componente Comercialización)
   - Fórmula: EC = Σ(injection) × C

3. **EE1 (Excedentes Tipo 1 - Compensación)**:
   - Cantidad: min(Σ injection, Σ consumption) por servicio y mes
   - Tarifa: -CU (negativo)
   - Fórmula: EE1 = min(Σ injection, Σ consumption) × (-CU)
   - Justificación: Compensa energía inyectada hasta el nivel de consumo

4. **EE2 (Excedentes Tipo 2 - Precio de Bolsa)**:
   - Cantidad: Si Σ injection > Σ consumption, entonces Σ(max(0, injection_hora - consumption_hora)) por servicio, mes e HORA
   - Tarifa: Precio XM de xm_data (varía por hora)
   - Fórmula: EE2 = Σ_hora[max(0, injection_hora - consumption_hora) × XM_price_hora]
   - Justificación: Valora excedentes por encima del consumo a precio de mercado horario

### Reglas de Cruce de Tarifas
- **voltage_level = 1**: Cruce por (id_market, voltage_level, cdi)
- **voltage_level = 2 o 3**: Cruce por (id_market, voltage_level) - CDI se ignora

### Stack Tecnológico
- **Lenguaje**: Python 3.x
- **API**: FastAPI
- **ORM**: SQLAlchemy
- **BD**: SQLite (facturacion.db) - persistencia local
- **Procesamiento**: Pandas
- **Entorno**: Windows, desarrollo 100% local

### Decisiones Arquitectónicas
- Persistencia en SQLite para cumplir requisitos de entorno local
- Procesamiento mensual por id_service (agrupación temporal)
- Parsing robusto de fechas con pd.to_datetime
- Modelos SQLAlchemy normalizados con FK para integridad referencial

---

## Paso 2: Diseño de Estructura de Base de Datos ✓ (En progreso)

### Modelo Relacional Implementado

#### Tabla: tariffs (Maestro de Tarifas)
```
Columnas:
- id_market (PK, int): Identificador del mercado
- voltage_level (PK, int): Nivel de tensión (1, 2, 3)
- cdi (PK, int, nullable): Centro de Distribución (NULL para voltage_level 2/3)
- G, T, D, R, C, P (float): Componentes individuales del costo
- CU (float): Costo Unitario total
```
**Justificación**: PK compuesta para reflejar la lógica regulatoria. CDI anulable.

#### Tabla: services (Maestro de Puntos de Servicio)
```
Columnas:
- id_service (PK, int): ID único del servicio
- id_market (FK → tariffs.id_market, int)
- voltage_level (FK → tariffs.voltage_level, int)
- cdi (FK → tariffs.cdi, int, nullable)
```
**Justificación**: FK compuesta para garantizar que cada servicio pueda cruzarse con su tarifa correcta.

#### Tabla: records (Índice de Tiempo / Tabla Pivote)
```
Columnas:
- id_record (PK, int): ID único del registro horario
- id_service (FK → services.id_service, int)
- record_timestamp (datetime): Marca de tiempo de la medición (ISO format)
```
**Justificación**: Centraliza timestamps para cada servicio; permite agrupación mensual sin duplicados.

#### Tabla: consumption (Medición de Consumo)
```
Columnas:
- id_record (PK, FK → records.id_record, int): Referencia obligatoria a records
- value (float): Cantidad de kWh consumidos (3 decimales)
```
**Justificación**: Relación 1:1 con records. PK FK asegura que no hay duplicados.

#### Tabla: injection (Medición de Inyección)
```
Columnas:
- id_record (PK, FK → records.id_record, int): Referencia obligatoria a records
- value (float): Cantidad de kWh inyectados (3 decimales)
```
**Justificación**: Relación 1:1 con records. PK FK asegura que no hay duplicados.

#### Tabla: xm_data (Precios de Bolsa Horarios)
```
Columnas:
- record_timestamp (PK, datetime): Marca de tiempo (ISO format)
- value (float): Precio de bolsa en $/kWh (10 decimales)
```
**Justificación**: Lookup table para EE2. PK timestamp asegura un precio por hora.

### Árbol de Dependencias para Creación
1. tariffs (sin dependencias)
2. services (depende de tariffs)
3. records (depende de services)
4. consumption (depende de records)
5. injection (depende de records)
6. xm_data (sin dependencias)

### Representación en JSON del Esquema de Base de Datos

```json
{
  "database": "facturacion.db",
  "type": "SQLite",
  "tables": [
    {
      "name": "tariffs",
      "description": "Maestro de Tarifas - Componentes de costo por mercado",
      "primary_key": ["id_market", "voltage_level", "cdi"],
      "columns": {
        "id_market": {"type": "INTEGER", "nullable": false},
        "voltage_level": {"type": "INTEGER", "nullable": false, "values": [1, 2, 3]},
        "cdi": {"type": "INTEGER", "nullable": true, "note": "NULL para voltage_level 2,3"},
        "G": {"type": "FLOAT", "description": "Generación (COP/kWh)"},
        "T": {"type": "FLOAT", "description": "Transmisión (COP/kWh)"},
        "D": {"type": "FLOAT", "description": "Distribución (COP/kWh)"},
        "R": {"type": "FLOAT", "description": "Operación Red (COP/kWh)"},
        "C": {"type": "FLOAT", "description": "Comercialización (COP/kWh)"},
        "P": {"type": "FLOAT", "description": "Pérdidas (COP/kWh)"},
        "CU": {"type": "FLOAT", "description": "Costo Unitario Total (COP/kWh)"}
      },
      "records": 105
    },
    {
      "name": "services",
      "description": "Maestro de Puntos de Servicio - Clientes/usuarios",
      "primary_key": ["id_service"],
      "foreign_keys": {
        "id_market": "tariffs.id_market",
        "voltage_level": "tariffs.voltage_level",
        "cdi": "tariffs.cdi (nullable)"
      },
      "columns": {
        "id_service": {"type": "INTEGER", "nullable": false},
        "id_market": {"type": "INTEGER", "nullable": false},
        "voltage_level": {"type": "INTEGER", "nullable": false},
        "cdi": {"type": "INTEGER", "nullable": true}
      },
      "records": 3,
      "note": "Si voltage_level=2 o 3, CDI se ignora en cruce de tarifas"
    },
    {
      "name": "records",
      "description": "Índice de Tiempo - Registros horarios por servicio",
      "primary_key": ["id_record"],
      "foreign_keys": {
        "id_service": "services.id_service"
      },
      "columns": {
        "id_record": {"type": "INTEGER", "nullable": false},
        "id_service": {"type": "INTEGER", "nullable": false},
        "record_timestamp": {"type": "DATETIME", "format": "YYYY-MM-DD HH:MM:SS.ffffff"}
      },
      "records": 2160,
      "note": "Centraliza timestamps (2023-09-01 a 2023-09-30)"
    },
    {
      "name": "consumption",
      "description": "Medición de Consumo - Energía activa consumida de la red",
      "primary_key": ["id_record"],
      "foreign_keys": {
        "id_record": "records.id_record"
      },
      "columns": {
        "id_record": {"type": "INTEGER", "nullable": false},
        "value": {"type": "FLOAT", "unit": "kWh", "range": [0, 76.532]}
      },
      "records": 2160,
      "note": "Relación 1:1 con records"
    },
    {
      "name": "injection",
      "description": "Medición de Inyección - Energía exportada a la red",
      "primary_key": ["id_record"],
      "foreign_keys": {
        "id_record": "records.id_record"
      },
      "columns": {
        "id_record": {"type": "INTEGER", "nullable": false},
        "value": {"type": "FLOAT", "unit": "kWh", "range": [0, 27.962]}
      },
      "records": 2160,
      "note": "Relación 1:1 con records. 30.5% de registros tienen inyección > 0"
    },
    {
      "name": "xm_data",
      "description": "Precios de Bolsa Horarios - Para cálculo de EE2",
      "primary_key": ["record_timestamp"],
      "columns": {
        "record_timestamp": {"type": "DATETIME", "format": "YYYY-MM-DD HH:MM:SS.ffffff"},
        "value": {"type": "FLOAT", "unit": "COP/kWh", "range": [667.94, 1063.39]}
      },
      "records": 720,
      "note": "24 horas × 30 días. Lookup table para EE2"
    }
  ]
}
```

### Diagrama de Relaciones (ER)

```
┌─────────────────────────────────────────────────────────────────────┐
│                         SISTEMA AGPE - BD                           │
└─────────────────────────────────────────────────────────────────────┘

                            ┌──────────────────┐
                            │    tariffs       │
                            │ (105 registros)  │
                            ├──────────────────┤
                            │ id_market (PK)   │
                            │ voltage_level(PK)│
                            │ cdi (PK, nullable)
                            │ G, T, D, R, C, P │
                            │ CU               │
                            └────────┬──────────┘
                                     │ 1
                                     │ (FK compuesta)
                                     │
                    ┌────────────────▼─────────────────┐
                    │      services                    │
                    │   (3 registros - Clientes)       │
                    ├─────────────────────────────────┤
                    │ id_service (PK)                 │
                    │ id_market (FK)                  │
                    │ voltage_level (FK)              │
                    │ cdi (FK, nullable)              │
                    │                                 │
                    │ NOTA: Si voltage_level=2 o 3,  │
                    │       CDI se ignora en cruce    │
                    └────────────────┬─────────────────┘
                                     │ 1
                                     │ N
                                     │ (FK simple)
                                     │
                    ┌────────────────▼──────────────────────┐
                    │          records                      │
                    │   (2160 registros - Horarios)         │
                    ├───────────────────────────────────────┤
                    │ id_record (PK)                        │
                    │ id_service (FK → services)            │
                    │ record_timestamp (2023-09-01:30)      │
                    └──────┬──────────────────────┬──────────┘
                           │ 1:1                  │ 1:1
                           │                      │
            ┌──────────────▼────────┐  ┌──────────▼───────────────┐
            │   consumption         │  │    injection             │
            │ (2160 registros)      │  │  (2160 registros)        │
            ├──────────────────────┤  ├─────────────────────────┤
            │ id_record (PK, FK)   │  │ id_record (PK, FK)      │
            │ value (kWh)          │  │ value (kWh)             │
            │ Min: 0, Max: 76.5    │  │ Min: 0, Max: 27.96      │
            │ Prom: 14.2           │  │ Prom: 0.77, 659 > 0     │
            └──────────────────────┘  └─────────────────────────┘


┌─────────────────────────────────────────────────────────────────┐
│                   xm_data (Sin relaciones FK)                   │
│                 (720 registros - Precios Bolsa)                 │
├─────────────────────────────────────────────────────────────────┤
│ record_timestamp (PK) | value (COP/kWh)                         │
│ 2023-09-01 00:00:00   | 815.78                                  │
│ ... (24h × 30 días)   | 667.94 - 1063.39                        │
└─────────────────────────────────────────────────────────────────┘
```

### Por Qué el Modelo se Ve Así (Justificación)

**1. PK Compuesta en tariffs (id_market, voltage_level, cdi)**
   - Razón: Garantiza combinaciones únicas regulatoriamente válidas
   - Beneficio: Imposible insertar tarifas duplicadas
   - Ejemplo: (id_market=1, voltage_level=1, cdi=100) ≠ (id_market=1, voltage_level=1, cdi=50)

**2. CDI Nullable en tariffs y services**
   - Razón: Para voltage_level 2 y 3, el CDI no aplica (regulación CREG)
   - Implementación: PK permite NULL; services ignora CDI para cruce si voltage_level=2/3
   - Beneficio: Un solo esquema para todos los niveles

**3. FK Compuesta en services**
   - Razón: Asegurar que cada servicio cruza con su tarifa correcta
   - Validación: SQLAlchemy rechaza services que no tengan tariff coincidente
   - Garantía: Integridad referencial automática

**4. Records como Tabla Pivote**
   - Razón: Centralizar timestamps para evitar duplicación de datos
   - Beneficio: Facilita agrupación mensual y búsqueda temporal
   - Escalabilidad: Agregar nuevas mediciones sin cambiar estructura

**5. Consumption e Injection como Tablas Separadas**
   - Razón: Cada registro puede tener consumo, inyección, o ambos
   - Flexibilidad: Nullable implícito (si no existe registro, es NULL)
   - Normalización: Evita columnas de valores que podrían ser NULL

**6. XM Data como Lookup Table**
   - Razón: Precios horarios para cálculo de EE2 (excedentes tipo 2)
   - Independencia: No tiene FK porque no es específica de un servicio
   - Reutilización: Un precio por hora para todos los servicios

### Ubicación de Cada Tabla en el Código

| Tabla | Archivo | Líneas | Clase SQLAlchemy |
|-------|---------|--------|------------------|
| tariffs | `models.py` | 17-38 | `class Tariff(Base)` |
| services | `models.py` | 41-56 | `class Service(Base)` |
| records | `models.py` | 59-74 | `class Record(Base)` |
| consumption | `models.py` | 77-85 | `class Consumption(Base)` |
| injection | `models.py` | 88-96 | `class Injection(Base)` |
| xm_data | `models.py` | 99-108 | `class XmData(Base)` |

**Carga de Datos**:
- `etl.py`: Funciones `parse_*()` para leer CSVs
- `etl.py`: Funciones `load_*()` para insertar en BD

**Validación**:
- `validate_db.py`: Integridad referencial y estadísticas

---

## Paso 3: ETL de Datos ✓ (Completado)

### Implementación y Resultados

**Archivo**: `etl.py`

**Funcionalidad**:
- Lectura de CSVs con Pandas usando `pd.read_csv()`
- Parsing robusto de tipos de datos:
  - Integers: id_market, id_service, voltage_level, cdi
  - Floats: Componentes tarifarios y valores de energía
  - DateTime: `pd.to_datetime()` con formato '%Y-%m-%d %H:%M:%S.%f'
  - Nullable integers: cdi con `pd.to_numeric(..., errors='coerce').astype('Int64')`
- Carga respetando árbol de dependencias:
  1. tariffs (sin dependencias)
  2. services (FK → tariffs)
  3. records (FK → services)
  4. consumption (FK → records)
  5. injection (FK → records)
  6. xm_data (sin dependencias)

**Validación de Carga** (Confirmado):
- ✓ Tariffs: 105 registros (mercados 1-10, voltage_levels 1-3, cdi variables)
- ✓ Services: 3 registros (id_service: 3222, 2256, 2478)
- ✓ Records: 2160 registros (timestamps 2023-09-01 a 2023-09-30)
- ✓ Consumption: 2160 registros (valores 0.50-62.62 kWh)
- ✓ Injection: 2160 registros (mayormente 0.0)
- ✓ XM Data: 720 registros (precios 815.78 COP/kWh)

**Base de Datos Creada**: `facturacion.db` (SQLite)

### Justificación Técnica
- SQLAlchemy ORM para abstracción DB-agnóstica (escalable a PostgreSQL si se requiere)
- PK compuestas en tariffs para garantizar combinaciones únicas (id_market, voltage_level, cdi)
- FKs compuestas en services para cumplir reglas de cruce tarifario
- Parsing explícito de DateTime para evitar ambigüedad de formatos
- Validación de integridad referencial automática por SQLAlchemy

---

## Paso 4: Validación de Integridad de Datos ✓ (Completado)

### Archivo: `validate_db.py`

### Resultados de Validación

**Tabla Tariffs**:
- ✓ Total: 105 registros
- ✓ Combinaciones únicas (id_market, voltage_level, cdi): 105 (sin duplicados)
- ✓ Tariffs nivel 2/3 con cdi NULL: Todos (validación de lógica regulatoria)

**Tabla Services**:
- ✓ Total: 3 registros
- ✓ Huérfanos (sin tariff FK): 0
- Servicios cargados:
  - id_service=2256, mercado 1, nivel 1, cdi=100
  - id_service=2478, mercado 1, nivel 1, cdi=0
  - id_service=3222, mercado 4, nivel 2, cdi=101 (ignorado para cruce)

**Tabla Records**:
- ✓ Total: 2160 registros
- ✓ Huérfanos (sin service FK): 0
- ✓ Rango temporal: 2023-09-01 00:00:00 a 2023-09-30 23:00:00 (30 días × 24 horas × 3 servicios)

**Tabla Consumption**:
- ✓ Total: 2160 registros (cobertura 100%)
- ✓ Huérfanos (sin record FK): 0
- Estadísticas:
  - Mín: 0.000 kWh
  - Promedio: 14.219 kWh
  - Máx: 76.532 kWh

**Tabla Injection**:
- ✓ Total: 2160 registros (cobertura 100%)
- ✓ Huérfanos (sin record FK): 0
- Estadísticas:
  - Mín: 0.000 kWh
  - Promedio: 0.772 kWh
  - Máx: 27.962 kWh
  - Registros con inyección > 0: 659 (30.5% de los registros tienen inyección)

**Tabla XM Data**:
- ✓ Total: 720 registros (24 horas × 30 días)
- Estadísticas de precios:
  - Mín: 667.9444 COP/kWh
  - Promedio: 1017.5497 COP/kWh
  - Máx: 1063.3861 COP/kWh

**Cobertura Temporal**:
- ✓ Records: 2023-09-01 a 2023-09-30 (30 días)
- ✓ XM Data: 2023-09-01 a 2023-09-30 (cobertura completa para EE2)

**Resumen por Servicio**:
1. Service 2256 (mercado 1, nivel 1):
   - 720 registros horarios
   - Consumo total: 381.77 kWh
   - Inyección total: 594.97 kWh (excede consumo, EE1 + EE2 aplicables)

2. Service 2478 (mercado 1, nivel 1):
   - 720 registros horarios
   - Consumo total: 562.97 kWh
   - Inyección total: 727.88 kWh (excede consumo, EE1 + EE2 aplicables)

3. Service 3222 (mercado 4, nivel 2):
   - 720 registros horarios
   - Consumo total: 29768.37 kWh
   - Inyección total: 344.86 kWh (muy por debajo del consumo, solo EE1 aplicable)

### Conclusiones de Validación
- ✓ Integridad referencial: Todas las FK válidas
- ✓ Cobertura de datos: 100% en consumption e injection
- ✓ Lógica regulatoria: CDI NULL para niveles 2/3 confirmado
- ✓ Datos listos para cálculo de conceptos (EA, EC, EE1, EE2)

---

## Paso 5: Lógica de Cálculo Modular (Completado ✅)
Se desarrolló `billing_engine.py` de forma modular y con aislamiento de conceptos matemáticos, logrando extraer los datos de SQLite y calculando usando la vectorización de Pandas de forma eficiente.

## Paso 6: API RESTful con FastAPI (Completado ✅)
Se desarrolló el stack de comunicación HTTP en `main.py` empleando FastAPI exigiendo seguridad mediante variable de entorno `.env` (`x-api-key`). El esquema responde a:

1. **`POST /calculate-invoice`**: Retorna dict completo de la factura.
2. **`GET /client-statistics/{service_id}`**: Interfaz analítica.
3. **`GET /system-load`**: Muestra la carga hora por hora.
4. **`GET /calculate-concept/{service_id}?concept=EA`**: El endpoint independiente.

## Paso 7: Despliegue y Ejecución Local (Completado ✅)
Se implementó `Guia_Ejecucion_Local_API.md` listando exactamente cómo inicializar uvicorn, leer las variables de entorno y consumirlo mediante cURL.

---

## 🚀 Guía de Hand-off: Cómo Replicar este Repositorio
Esta es la instrucción exacta si le pasas esta carpeta a otro evaluador o analista para que pruebe todo de cero en su propia computadora local con Windows o Mac:

1. **Instalar Dependencias**:
   `pip install pandas sqlalchemy fastapi uvicorn pydantic python-dotenv requests`
2. **Generar la Base de Datos**:
   Ejecutar `python etl.py`. *(Espera a que tome los CSVs y reconstruya `facturacion.db` desde cero)*.
3. **Validar Salud de Datos** (Opcional):
   Ejecutar `python validate_db.py` para constatar integridad referencial.
4. **Levantar el Servidor API**:
   Ejecutar `python -m uvicorn main:app --port 8000 --reload`
5. **Utilizar Interfaz Gráfica o Manual**:
   El colega puede abrir `http://127.0.0.1:8000/docs` en su navegador o puedes referirlo al archivo `Guia_Ejecucion_Local_API.md` para que use CURL. Ambos le exigirán usar el header `x-api-key: agpe_erco_secret_key_12345`.
6. **Ejecutar Pruebas de Estrés HTTP**:
   Puede correr el archivo temporal `test_api.py` para ver 5 pruebas aisladas de la API. Log esperado:
   
   ```json
   --- PRUEBA 1: Factura Completa Usuario 2256 ---
   { "service_id": 2256, "EA": 294241.59, "EC": 14243.58, "EE1": -294241.59, "EE2": 225869.29, "month": "2023-09" }
   
   --- PRUEBA 2: Concepto Independiente (EE2) Usuario 2478 ---
   { "service_id": 2478, "concept_requested": "EE2", "monetary_value_COP": 174350.73 }
   
   --- PRUEBA 3: Estadísticas Analíticas Usuario 3222 ---
   { "service_id": 3222, "total_activa_mensual": 29768.373, "hora_pico_consumo": "2023-09-12 16:00:00" }
   ```

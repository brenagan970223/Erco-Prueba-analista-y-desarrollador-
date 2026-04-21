# Diccionario y Análisis de Datos - Sistema AGPE

Este documento proporciona una radiografía completa de la información contenida en los datasets (CSVs / Tablas) del proyecto, detallando la volumetría, estructura de columnas y el papel que juegan en el ecosistema de facturación de energía para generar mayor contexto.

---

## 1. Clientes y Generadores (Tabla: `services`)
**Archivo Origen:** `services 4.csv`
**Volumetría:** 3 filas (usuarios) × 4 columnas.

**Descripción del Negocio:**
Representa el maestro de los "Autogeneradores a Pequeña Escala" (usuarios físicos). Describe a qué mercado pertenecen y qué infraestructura técnica de conexión tienen (Nivel de tensión).

| Columna | Tipo | Descripción |
|---|---|---|
| `id_service` | Integer (PK) | Identificador único del cliente. Tenemos exactamente 3 clientes (IDs: **2256**, **2478**, **3222**). |
| `id_market` | Integer (FK) | Mercado al que pertenece. Ej: Mercado 1 y Mercado 4. |
| `voltage_level` | Integer (FK) | Nivel de tensión de la red (1, 2 o 3). |
| `cdi` | Integer (FK) | Centro de Distribución. *Nota: Nulo/Ignorado si el Nivel de tensión es 2 o 3*. |

---

## 2. Catálogo de Precios Regulados (Tabla: `tariffs`)
**Archivo Origen:** `tariffs 4.csv`
**Volumetría:** 105 filas (tarifas únicas) × 10 columnas.

**Descripción del Negocio:**
Almacena los componentes económicos regulados. Una tarifa no se le asigna a un usuario de manera directa u obvia, sino que se *calcula dinámicamente* cruzando tres variables de su servicio: mercado, tensión y CDI.

| Columna | Tipo | Descripción |
|---|---|---|
| `id_market` | Integer (PK) | Numerados del mercado 1 al 10 en la data. |
| `voltage_level`| Integer (PK) | Nivel 1, 2 o 3. |
| `cdi` | Integer (PK) | Clave adicional requerida solo para el Nivel 1. |
| `G, T, D, R, C, P` | Float | Componentes técnicos de la tarifa COP/kWh (Generación, Transmisión, Distribución, Red, Comercialización y Pérdidas). |
| `CU` | Float | Costo Unitario total (Suma de los anteriores). Base principal para cobrar el consumo de red (EA) y reconocer el excedente base (EE1). |

---

## 3. Línea Base Temporal (Tabla: `records`)
**Archivo Origen:** `records 4.csv`
**Volumetría:** 2160 filas × 3 columnas.

**Descripción del Negocio:**
Es la tabla cruzada o columna vertebral temporal. Mapea exactamente cada hora de un mes para cada cliente, sirviendo como llave central indispensable para anclar los valores de consumos e inyecciones sin repetir fechas inútilmente.
*(Justificación matemática: 30 días de Septiembre × 24 horas × 3 clientes = 2160 registros exactos).*

| Columna | Tipo | Descripción |
|---|---|---|
| `id_record` | Integer (PK) | Identificador secuencial individual del registro. |
| `id_service` | Integer (FK) | Cliente al que se le tomó la foto horaria. |
| `record_timestamp` | DateTime | Fecha y hora exacta (desde `2023-09-01 00:00:00` hasta `2023-09-30 23:00:00`). |

---

## 4. Medidores de Consumo (Tabla: `consumption`)
**Archivo Origen:** `consumption 4.csv`
**Volumetría:** 2160 filas × 2 columnas.

**Descripción del Negocio:**
Los kilovatios-hora (kWh) que los clientes extrajeron de la infraestructura eléctrica nacional convencional.

| Columna | Tipo | Descripción | Estadísticas Reales del Dataset |
|---|---|---|---|
| `id_record` | Integer (PK/FK) | Enlace de tiempo 1 a 1 | **Cobertura:** 100% de los records (No hay nulos) |
| `value` | Float | kWh consumidos en esa hora | **Mínimo:** 0.0<br>**Promedio general:** 14.21 kWh<br>**Máximo pico:** 76.53 kWh |

---

## 5. Excedentes Solares / Medidor Bi-Direccional (Tabla: `injection`)
**Archivo Origen:** `injection 4.csv`
**Volumetría:** 2160 filas × 2 columnas.

**Descripción del Negocio:**
Los excedentes solares (generación limpia del cliente) que superaron lo usado en su hogar y "regresaron" obligatoriamente inyectándose en la red. Esta es la base monetaria del negocio para el usuario generador.

| Columna | Tipo | Descripción | Estadísticas Reales del Dataset |
|---|---|---|---|
| `id_record` | Integer (PK/FK) | Enlace de tiempo 1 a 1 | **Cobertura:** 100% registros listados |
| `value` | Float | kWh inyectados en esa hora | **Horas con Inyección Real (>0):** ~659 horas (Apenas el 30.5% del mes inyectan)<br>**Máximo Inyectado:** 27.96 kWh |

---

## 6. Dinámica de Mercado Bursátil (Tabla: `xm_data`)
**Archivo Origen:** `xm_data_hourly_per_agent 4.csv`
**Volumetría:** 720 filas × 2 columnas.

**Descripción del Negocio:**
Precio variable de la energía transada en la bolsa de valores durante el mes hora a hora. Se compone de las 720 horas naturales del mes. Se usa exclusivamente para pagarle los kWh sobrantes masivos (EE2) al cliente cuando en términos totales mensuales ya despachó más de lo que gastó, siendo el precio horario de "recompensa".

| Columna | Tipo | Descripción | Estadísticas Reales del Dataset |
|---|---|---|---|
| `record_timestamp`| DateTime (PK) | Hora exacta en la bolsa | Del 1 al 30 de septiembre 2023. |
| `value` | Float | COP / kWh en bolsa en ese instante | **Mínimo:** $667.94<br>**Promedio:** $1017.54<br>**Máximo pico:** $1063.38 |

---

## 🚀 Insights Analíticos y Estructurales (Crucial para Entender el Procesamiento)

1. **Perfiles Divergentes de Cliente:**
   * El cliente **`3222`** consume cantidades industriales (29,768 kWh al mes) pero inyecta poquísimo (344 kWh). Para él, el cálculo cronológico es irrelevante porque nunca superará su meta: **tendrá EE2 = 0** siempre.
   * El cliente **`2256`** es el perfil superavitario: consume solo 381 kWh e inyecta casi el doble (594 kWh). Este es el usuario que someterá al código de la API al límite algorítmico, ya que activará el cruce contra `xm_data` obligatoriamente a mitad de mes.

2. **Beneficio del Esquema Relacional Uno a Uno:**
   La estructura de separar *consumption* e *injection* ligándolas al mismo `id_record` permite crear una tabla plana gigante matricial durante nuestros cálculos (como lo hace `billing_engine.py`) de la forma:
   `[Fecha y Hora] | [Consumo Casa] | [Producción Inyectada] | [Precio Bolsa Hora]`.
   
   Esa "aplanada" técnica es la que nos permite detectar el segundo exacto (hora de quiebre cronológica) sin caer en loops anidados que rompan los servidores cuando escalemos a un millón de clientes, aprovechando toda la librería Pandas.

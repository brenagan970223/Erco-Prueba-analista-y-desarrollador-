Documentación Técnica: Sistema de Liquidación AGPE ⚡
Line Spacing: 1.25
1. Resumen del Proyecto
Este sistema automatiza la liquidación de facturas para Autogeneradores a Pequeña Escala (AGPE). El motor procesa registros horarios de consumo e inyección para determinar cargos y créditos basados en la normativa vigente, utilizando una arquitectura desacoplada y portable en Python.
2. Diseño de la Base de Datos (Esquema Relacional)
Siguiendo el diseño técnico solicitado, el sistema implementa una base de datos relacional normalizada para optimizar el procesamiento de series de tiempo:
Entidad
	Relación / Función
	Origen de Datos (CSV)
 
	services
	Maestro de clientes. Conecta con tariffs e indexa los records.
	services 4.csv
	records
	Tabla pivote temporal. Asocia un timestamp a un servicio.
	records 4.csv
	consumption
	Relación 1:1 con records. Almacena kWh consumidos de la red.
	consumption 4.csv
	injection
	Relación 1:1 con records. Almacena kWh exportados a la red.
	injection 4.csv
	tariffs
	Maestro de precios. Contiene el desglose de CU (G, T, D, R, C, P).
	tariffs 4.csv
	xm_data
	Precios de bolsa horarios para el cálculo de excedentes tipo 2 (EE2).
	xm_data_hourly_per_agent 4.csv
	3. Lógica Regulatoria Específica
* Cruce de Tarifas:
   * Si voltage_level es 1: Se requiere coincidencia de id_market, voltage_level y cdi.
   * Si voltage_level es 2 o 3: El cdi es irrelevante; se cruza solo por id_market y voltage_level.
* Conceptos de Liquidación:
   * EA: Consumo total mensual × CU.
   * EC: Inyección total mensual × Componente C (Comercialización).
   * EE1: Energía inyectada compensada a precio CU.
   * EE2: Energía inyectada excedente valorada a precio de bolsa horario (XM).
4. Guía de Ejecución y Preparación
Para ejecutar el proyecto hasta este punto, siga estos pasos en su terminal:
Paso 1: Instalación de Entorno
python -m pip install fastapi uvicorn pandas sqlalchemy pydantic
Paso 2: Estructura del Proyecto
Asegúrese de que los archivos CSV se encuentren en la misma carpeta que sus scripts de Python para permitir la ingesta automática.
Paso 3: Próxima Fase (ETL)
El siguiente paso consiste en ejecutar el script de carga que mapea los DataFrames de Pandas a las tablas de SQLAlchemy en el archivo facturacion.db.
Este documento sirve como especificación técnica para el desarrollo del backend Middle.
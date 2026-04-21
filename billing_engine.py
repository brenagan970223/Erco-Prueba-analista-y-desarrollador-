import pandas as pd
import os
from sqlalchemy import create_engine

# --- CONFIGURACIÓN DE DB ---
def get_db_engine(data_dir='.'):
    db_path = os.path.join(data_dir, 'facturacion.db')
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"La BD {db_path} no existe. Ejecuta etl.py primero.")
    return create_engine(f'sqlite:///{db_path}')

# --- CORE DATA EXTRACTOR ---
def _get_service_data(service_id: int, data_dir: str = '.'):
    """
    Función base que consulta la BD y ensambla el dataframe central para un servicio,
    además de obtener su tarifa. Esto centraliza las queries y la lógica de cruce.
    """
    engine = get_db_engine(data_dir)
    
    # Extraemos solo lo necesario desde SQL
    services = pd.read_sql(f"SELECT * FROM services WHERE id_service = {service_id}", engine)
    if services.empty:
        raise ValueError(f"Servicio {service_id} no encontrado.")
    service = services.iloc[0]
    
    # Tarifa
    v_level = int(service['voltage_level'])
    market = int(service['id_market'])
    if v_level in [2, 3]:
        tariff_query = f"SELECT * FROM tariffs WHERE id_market = {market} AND voltage_level = {v_level}"
    else:
        cdi = service['cdi']
        tariff_query = f"SELECT * FROM tariffs WHERE id_market = {market} AND voltage_level = {v_level} AND cdi = {cdi}"
        
    tariffs = pd.read_sql(tariff_query, engine)
    if tariffs.empty:
        raise ValueError("Tarifa no encontrada.")
    tariff = tariffs.iloc[0]
    
    CU = float(tariff['CU'])
    C_tariff = float(tariff['C'])
    
    # Registros, Consumos e Inyecciones específicos de este servicio
    records = pd.read_sql(f"SELECT * FROM records WHERE id_service = {service_id}", engine)
    records['record_timestamp'] = pd.to_datetime(records['record_timestamp'])
    records = records.sort_values('record_timestamp')
    
    # Extraer los id_record para usarlos de filtro (optimizacion)
    record_ids = tuple(records['id_record'].tolist())
    if not record_ids:
         raise ValueError("No hay registros temporales para este servicio.")
         
    # Convertimos al formato (id1, id2...) para query SQL
    ids_str = ','.join(map(str, record_ids))
    consumption = pd.read_sql(f"SELECT * FROM consumption WHERE id_record IN ({ids_str})", engine)
    injection = pd.read_sql(f"SELECT * FROM injection WHERE id_record IN ({ids_str})", engine)
    
    # Unir consumo
    df = pd.merge(records, consumption, on='id_record', how='left')
    df.rename(columns={'value': 'cons_value'}, inplace=True)
    df['cons_value'] = df['cons_value'].fillna(0.0)
    
    # Unir inyección
    df = pd.merge(df, injection, on='id_record', how='left')
    df.rename(columns={'value': 'inj_value'}, inplace=True)
    df['inj_value'] = df['inj_value'].fillna(0.0)
    
    return df, CU, C_tariff, engine

# --- FUNCIONES MATEMÁTICAS INDEPENDIENTES (MODULARES) ---

def math_EA(df: pd.DataFrame, CU: float) -> float:
    return float(df['cons_value'].sum() * CU)

def math_EC(df: pd.DataFrame, C_tariff: float) -> float:
    return float(df['inj_value'].sum() * C_tariff)

def math_EE1(df: pd.DataFrame, CU: float) -> float:
    return float(min(df['inj_value'].sum(), df['cons_value'].sum()) * (-CU))

def math_EE2(df: pd.DataFrame, engine) -> float:
    total_consumption = df['cons_value'].sum()
    total_injection = df['inj_value'].sum()
    qty_EE2 = max(0.0, total_injection - total_consumption)
    
    if qty_EE2 <= 0:
        return 0.0
        
    xm_data = pd.read_sql("SELECT * FROM xm_data", engine)
    xm_data['record_timestamp'] = pd.to_datetime(xm_data['record_timestamp'])
    
    df_ee2 = pd.merge(df, xm_data, on='record_timestamp', how='left')
    df_ee2.rename(columns={'value': 'xm_price'}, inplace=True)
    df_ee2['xm_price'] = df_ee2['xm_price'].fillna(0.0)
    
    df_ee2['cumsum_inj'] = df_ee2['inj_value'].cumsum()
    df_ee2['prev_cumsum_inj'] = df_ee2['cumsum_inj'].shift(1, fill_value=0.0)
    
    def calculate_hourly_ee2(row):
        if row['prev_cumsum_inj'] >= total_consumption:
            return row['inj_value'] * row['xm_price']
        elif row['cumsum_inj'] > total_consumption:
            return (row['cumsum_inj'] - total_consumption) * row['xm_price']
        return 0.0
        
    return float(df_ee2.apply(calculate_hourly_ee2, axis=1).sum())

# --- ENDPOINT LOGIC: CALCULAR FACTURA COMPLETA ---
def calculate_invoice(service_id: int, data_dir: str = '.'):
    df, CU, C_tariff, engine = _get_service_data(service_id, data_dir)
    
    return {
        "service_id": service_id,
        "EA": round(math_EA(df, CU), 2),
        "EC": round(math_EC(df, C_tariff), 2),
        "EE1": round(math_EE1(df, CU), 2),
        "EE2": round(math_EE2(df, engine), 2),
        "Total_Consumo_kWh": round(df['cons_value'].sum(), 3),
        "Total_Inyeccion_kWh": round(df['inj_value'].sum(), 3)
    }

# --- ENDPOINT LOGIC: CÁLCULO INDEPENDIENTE DE UN CONCEPTO ---
def calculate_single_concept(service_id: int, concept: str, data_dir: str = '.'):
    df, CU, C_tariff, engine = _get_service_data(service_id, data_dir)
    concept = concept.upper()
    if concept == "EA":
        return round(math_EA(df, CU), 2)
    elif concept == "EC":
        return round(math_EC(df, C_tariff), 2)
    elif concept == "EE1":
        return round(math_EE1(df, CU), 2)
    elif concept == "EE2":
        return round(math_EE2(df, engine), 2)
    else:
        raise ValueError("Concepto inválido. Usa EA, EC, EE1, o EE2.")

# --- ENDPOINT LOGIC: CLIENT STATISTICS ---
def get_client_statistics(service_id: int, data_dir: str = '.'):
    df, _, _, _ = _get_service_data(service_id, data_dir)
    consumo_max = df.loc[df['cons_value'].idxmax()]
    inyeccion_max = df.loc[df['inj_value'].idxmax()]
    
    return {
        "service_id": service_id,
        "total_activa_mensual": round(df['cons_value'].sum(), 3),
        "total_inyeccion_mensual": round(df['inj_value'].sum(), 3),
        "promedio_consumo_hora": round(df['cons_value'].mean(), 3),
        "pico_maximo_consumo_kwh": round(consumo_max['cons_value'], 3),
        "hora_pico_consumo": str(consumo_max['record_timestamp']),
        "pico_maximo_inyeccion_kwh": round(inyeccion_max['inj_value'], 3),
        "horas_con_inyeccion_positiva": int((df['inj_value'] > 0).sum())
    }

# --- ENDPOINT LOGIC: SYSTEM LOAD ---
def get_system_load(data_dir: str = '.'):
    engine = get_db_engine(data_dir)
    # Requerimiento: "Muestra la carga del sistema por hora basada en consumo"
    # Unimos records con consumption agrupando por hora de todos los records
    query = """
    SELECT r.record_timestamp, SUM(c.value) as system_load_kwh
    FROM records r
    JOIN consumption c ON r.id_record = c.id_record
    GROUP BY r.record_timestamp
    ORDER BY r.record_timestamp ASC
    """
    df_load = pd.read_sql(query, engine)
    
    # Formateamos para devolver como una lista/dict amigable para la API web
    return df_load.to_dict(orient='records')

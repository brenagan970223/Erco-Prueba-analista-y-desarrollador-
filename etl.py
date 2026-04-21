import pandas as pd
from sqlalchemy.orm import sessionmaker
from models import init_db, Tariff, Service, Record, Consumption, Injection, XmData
from datetime import datetime
import os

# Configuración
DB_PATH = 'facturacion.db'
CSV_DIR = '.'  # Mismo directorio que este script

# Mapeo de CSV a columnas esperadas
CSV_FILES = {
    'tariffs': 'tariffs 4.csv',
    'services': 'services 4.csv',
    'records': 'records 4.csv',
    'consumption': 'consumption 4.csv',
    'injection': 'injection 4.csv',
    'xm_data': 'xm_data_hourly_per_agent 4.csv'
}


def parse_tariffs():
    """Carga tariffs desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['tariffs']))
    
    # Conversión de tipos
    df['id_market'] = df['id_market'].astype(int)
    df['voltage_level'] = df['voltage_level'].astype(int)
    df['cdi'] = pd.to_numeric(df['cdi'], errors='coerce').astype('Int64')  # Nullable int
    
    # Convertir float components
    for col in ['G', 'T', 'D', 'R', 'C', 'P', 'CU']:
        df[col] = df[col].astype(float)
    
    print(f"✓ Tariffs cargado: {len(df)} registros")
    return df


def parse_services():
    """Carga services desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['services']))
    
    df['id_service'] = df['id_service'].astype(int)
    df['id_market'] = df['id_market'].astype(int)
    df['voltage_level'] = df['voltage_level'].astype(int)
    df['cdi'] = pd.to_numeric(df['cdi'], errors='coerce').astype('Int64')  # Nullable int
    
    print(f"✓ Services cargado: {len(df)} registros")
    return df


def parse_records():
    """Carga records desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['records']))
    
    df['id_record'] = df['id_record'].astype(int)
    df['id_service'] = df['id_service'].astype(int)
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    
    print(f"✓ Records cargado: {len(df)} registros")
    return df


def parse_consumption():
    """Carga consumption desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['consumption']))
    
    df['id_record'] = df['id_record'].astype(int)
    df['value'] = df['value'].astype(float)
    
    print(f"✓ Consumption cargado: {len(df)} registros")
    return df


def parse_injection():
    """Carga injection desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['injection']))
    
    df['id_record'] = df['id_record'].astype(int)
    df['value'] = df['value'].astype(float)
    
    print(f"✓ Injection cargado: {len(df)} registros")
    return df


def parse_xm_data():
    """Carga xm_data desde CSV."""
    df = pd.read_csv(os.path.join(CSV_DIR, CSV_FILES['xm_data']))
    
    df['record_timestamp'] = pd.to_datetime(df['record_timestamp'], format='%Y-%m-%d %H:%M:%S.%f')
    df['value'] = df['value'].astype(float)
    
    print(f"✓ XM Data cargado: {len(df)} registros")
    return df


def load_tariffs(session, df):
    """Inserta tariffs en la BD."""
    for _, row in df.iterrows():
        tariff = Tariff(
            id_market=int(row['id_market']),
            voltage_level=int(row['voltage_level']),
            cdi=int(row['cdi']) if pd.notna(row['cdi']) else None,
            G=float(row['G']),
            T=float(row['T']),
            D=float(row['D']),
            R=float(row['R']),
            C=float(row['C']),
            P=float(row['P']),
            CU=float(row['CU'])
        )
        session.add(tariff)
    
    session.commit()
    print(f"✓ Tariffs insertados: {df.shape[0]} registros en BD")


def load_services(session, df):
    """Inserta services en la BD."""
    for _, row in df.iterrows():
        service = Service(
            id_service=int(row['id_service']),
            id_market=int(row['id_market']),
            voltage_level=int(row['voltage_level']),
            cdi=int(row['cdi']) if pd.notna(row['cdi']) else None
        )
        session.add(service)
    
    session.commit()
    print(f"✓ Services insertados: {df.shape[0]} registros en BD")


def load_records(session, df):
    """Inserta records en la BD."""
    for _, row in df.iterrows():
        record = Record(
            id_record=int(row['id_record']),
            id_service=int(row['id_service']),
            record_timestamp=row['record_timestamp']
        )
        session.add(record)
    
    session.commit()
    print(f"✓ Records insertados: {df.shape[0]} registros en BD")


def load_consumption(session, df):
    """Inserta consumption en la BD."""
    for _, row in df.iterrows():
        consumption = Consumption(
            id_record=int(row['id_record']),
            value=float(row['value'])
        )
        session.add(consumption)
    
    session.commit()
    print(f"✓ Consumption insertados: {df.shape[0]} registros en BD")


def load_injection(session, df):
    """Inserta injection en la BD."""
    for _, row in df.iterrows():
        injection = Injection(
            id_record=int(row['id_record']),
            value=float(row['value'])
        )
        session.add(injection)
    
    session.commit()
    print(f"✓ Injection insertados: {df.shape[0]} registros en BD")


def load_xm_data(session, df):
    """Inserta xm_data en la BD."""
    for _, row in df.iterrows():
        xm = XmData(
            record_timestamp=row['record_timestamp'],
            value=float(row['value'])
        )
        session.add(xm)
    
    session.commit()
    print(f"✓ XM Data insertados: {df.shape[0]} registros en BD")


def main():
    """ETL principal: carga todos los CSVs en orden de dependencias."""
    
    print("=" * 60)
    print("INICIANDO ETL - Sistema de Liquidación AGPE")
    print("=" * 60)
    
    # Paso 1: Inicializar BD
    print("\n[1/8] Inicializando base de datos...")
    engine = init_db(DB_PATH)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # Paso 2-7: Parsear CSVs
    print("\n[2/8] Parseando CSV de tariffs...")
    df_tariffs = parse_tariffs()
    
    print("[3/8] Parseando CSV de services...")
    df_services = parse_services()
    
    print("[4/8] Parseando CSV de records...")
    df_records = parse_records()
    
    print("[5/8] Parseando CSV de consumption...")
    df_consumption = parse_consumption()
    
    print("[6/8] Parseando CSV de injection...")
    df_injection = parse_injection()
    
    print("[7/8] Parseando CSV de xm_data...")
    df_xm_data = parse_xm_data()
    
    # Paso 8: Cargar en BD respetando dependencias
    print("\n[8/8] Cargando datos en BD (orden de dependencias)...")
    print("\n  • Insertando tariffs...")
    load_tariffs(session, df_tariffs)
    
    print("  • Insertando services...")
    load_services(session, df_services)
    
    print("  • Insertando records...")
    load_records(session, df_records)
    
    print("  • Insertando consumption...")
    load_consumption(session, df_consumption)
    
    print("  • Insertando injection...")
    load_injection(session, df_injection)
    
    print("  • Insertando xm_data...")
    load_xm_data(session, df_xm_data)
    
    # Validación final
    print("\n" + "=" * 60)
    print("VALIDACIÓN DE CARGA")
    print("=" * 60)
    
    tariffs_count = session.query(Tariff).count()
    services_count = session.query(Service).count()
    records_count = session.query(Record).count()
    consumption_count = session.query(Consumption).count()
    injection_count = session.query(Injection).count()
    xm_count = session.query(XmData).count()
    
    print(f"\n✓ Tariffs en BD: {tariffs_count}")
    print(f"✓ Services en BD: {services_count}")
    print(f"✓ Records en BD: {records_count}")
    print(f"✓ Consumption en BD: {consumption_count}")
    print(f"✓ Injection en BD: {injection_count}")
    print(f"✓ XM Data en BD: {xm_count}")
    
    session.close()
    
    print("\n" + "=" * 60)
    print("✓ ETL COMPLETADO EXITOSAMENTE")
    print(f"✓ Base de datos: {DB_PATH}")
    print("=" * 60)


if __name__ == '__main__':
    main()

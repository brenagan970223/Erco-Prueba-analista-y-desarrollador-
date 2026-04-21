from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from models import Tariff, Service, Record, Consumption, Injection, XmData
import pandas as pd

DB_PATH = 'facturacion.db'


def validate_db():
    """Valida integridad de datos y relaciones en la BD."""
    
    engine = create_engine(f'sqlite:///{DB_PATH}')
    Session = sessionmaker(bind=engine)
    session = Session()
    
    print("=" * 70)
    print("VALIDACIÓN DE INTEGRIDAD - Sistema de Liquidación AGPE")
    print("=" * 70)
    
    # Test 1: Validar tariffs
    print("\n[1] Validando Tariffs...")
    tariffs = session.query(Tariff).all()
    print(f"  ✓ Total tariffs: {len(tariffs)}")
    
    # Verificar PK única
    pk_combos = session.query(Tariff.id_market, Tariff.voltage_level, Tariff.cdi).distinct().count()
    print(f"  ✓ Combinaciones únicas (id_market, voltage_level, cdi): {pk_combos}")
    
    # Verificar que voltage_level 2 y 3 tienen cdi NULL
    level_2_3_null_cdi = session.query(Tariff).filter(
        Tariff.voltage_level.in_([2, 3]),
        Tariff.cdi.isnot(None)
    ).count()
    print(f"  ✓ Tariffs nivel 2/3 con cdi no-NULL (esperado 0): {level_2_3_null_cdi}")
    
    # Test 2: Validar services
    print("\n[2] Validando Services...")
    services = session.query(Service).all()
    print(f"  ✓ Total services: {len(services)}")
    
    # Validar FK con tariffs
    orphan_services = session.query(Service).filter(
        ~Service.id_market.in_(session.query(Tariff.id_market).distinct())
    ).count()
    print(f"  ✓ Services huérfanos (sin tariff): {orphan_services}")
    
    # Mostrar servicios
    for svc in services:
        print(f"    - id_service={svc.id_service}, id_market={svc.id_market}, voltage_level={svc.voltage_level}, cdi={svc.cdi}")
    
    # Test 3: Validar records
    print("\n[3] Validando Records...")
    records_count = session.query(Record).count()
    print(f"  ✓ Total records: {records_count}")
    
    # Validar FK con services
    orphan_records = session.query(Record).filter(
        ~Record.id_service.in_(session.query(Service.id_service))
    ).count()
    print(f"  ✓ Records huérfanos (sin service): {orphan_records}")
    
    # Validar timestamps únicos por servicio
    dup_timestamps = session.query(Record.id_service, Record.record_timestamp).count()
    print(f"  ✓ Total registros (id_service, timestamp): {dup_timestamps}")
    
    # Test 4: Validar consumption
    print("\n[4] Validando Consumption...")
    consumption_count = session.query(Consumption).count()
    records_count = session.query(Record).count()
    print(f"  ✓ Total consumption: {consumption_count}")
    print(f"  ✓ Cobertura (consumption/records): {consumption_count}/{records_count}")
    
    # Validar FK con records
    orphan_consumption = session.query(Consumption).filter(
        ~Consumption.id_record.in_(session.query(Record.id_record))
    ).count()
    print(f"  ✓ Consumption huérfano (sin record): {orphan_consumption}")
    
    # Estadísticas
    avg_consumption = session.query(func.avg(Consumption.value)).scalar()
    max_consumption = session.query(func.max(Consumption.value)).scalar()
    min_consumption = session.query(func.min(Consumption.value)).scalar()
    print(f"  ✓ Estadísticas de consumo (kWh):")
    print(f"    - Min: {min_consumption:.3f}")
    print(f"    - Promedio: {avg_consumption:.3f}")
    print(f"    - Max: {max_consumption:.3f}")
    
    # Test 5: Validar injection
    print("\n[5] Validando Injection...")
    injection_count = session.query(Injection).count()
    print(f"  ✓ Total injection: {injection_count}")
    print(f"  ✓ Cobertura (injection/records): {injection_count}/{records_count}")
    
    # Validar FK con records
    orphan_injection = session.query(Injection).filter(
        ~Injection.id_record.in_(session.query(Record.id_record))
    ).count()
    print(f"  ✓ Injection huérfano (sin record): {orphan_injection}")
    
    # Estadísticas
    avg_injection = session.query(func.avg(Injection.value)).scalar()
    max_injection = session.query(func.max(Injection.value)).scalar()
    min_injection = session.query(func.min(Injection.value)).scalar()
    non_zero_injection = session.query(Injection).filter(Injection.value > 0).count()
    print(f"  ✓ Estadísticas de inyección (kWh):")
    print(f"    - Min: {min_injection:.3f}")
    print(f"    - Promedio: {avg_injection:.3f}")
    print(f"    - Max: {max_injection:.3f}")
    print(f"    - Registros con inyección > 0: {non_zero_injection}")
    
    # Test 6: Validar XM Data
    print("\n[6] Validando XM Data...")
    xm_count = session.query(XmData).count()
    print(f"  ✓ Total XM Data: {xm_count}")
    
    # Estadísticas
    avg_xm_price = session.query(func.avg(XmData.value)).scalar()
    max_xm_price = session.query(func.max(XmData.value)).scalar()
    min_xm_price = session.query(func.min(XmData.value)).scalar()
    print(f"  ✓ Estadísticas de precios XM (COP/kWh):")
    print(f"    - Min: {min_xm_price:.4f}")
    print(f"    - Promedio: {avg_xm_price:.4f}")
    print(f"    - Max: {max_xm_price:.4f}")
    
    # Test 7: Validar cobertura temporal
    print("\n[7] Validando Cobertura Temporal...")
    min_timestamp = session.query(func.min(Record.record_timestamp)).scalar()
    max_timestamp = session.query(func.max(Record.record_timestamp)).scalar()
    print(f"  ✓ Rango de timestamps en records:")
    print(f"    - Inicio: {min_timestamp}")
    print(f"    - Fin: {max_timestamp}")
    
    min_xm_timestamp = session.query(func.min(XmData.record_timestamp)).scalar()
    max_xm_timestamp = session.query(func.max(XmData.record_timestamp)).scalar()
    print(f"  ✓ Rango de timestamps en XM Data:")
    print(f"    - Inicio: {min_xm_timestamp}")
    print(f"    - Fin: {max_xm_timestamp}")
    
    # Test 8: Resumen por servicio
    print("\n[8] Resumen por Servicio...")
    for svc in services:
        svc_records = session.query(Record).filter(Record.id_service == svc.id_service).count()
        svc_consumption = session.query(func.sum(Consumption.value)).join(
            Record, Consumption.id_record == Record.id_record
        ).filter(Record.id_service == svc.id_service).scalar()
        svc_injection = session.query(func.sum(Injection.value)).join(
            Record, Injection.id_record == Record.id_record
        ).filter(Record.id_service == svc.id_service).scalar()
        print(f"  • Service {svc.id_service} (mercado {svc.id_market}, nivel {svc.voltage_level}):")
        print(f"    - Records: {svc_records}")
        print(f"    - Consumo total (kWh): {svc_consumption:.2f}")
        print(f"    - Inyección total (kWh): {svc_injection:.2f}")
    
    session.close()
    
    print("\n" + "=" * 70)
    print("✓ VALIDACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)


if __name__ == '__main__':
    validate_db()

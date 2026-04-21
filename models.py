from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Tariff(Base):
    """Maestro de Tarifas
    
    Almacena componentes de costo de energía por mercado, nivel de tensión y CDI.
    PK compuesta: (id_market, voltage_level, cdi) para reflejar lógica regulatoria.
    CDI es anulable para voltage_level 2 y 3.
    """
    __tablename__ = 'tariffs'
    
    id_market = Column(Integer, primary_key=True)
    voltage_level = Column(Integer, primary_key=True)
    cdi = Column(Integer, primary_key=True, nullable=True)
    
    # Componentes individuales del costo (COP/kWh)
    G = Column(Float, nullable=False)  # Generación
    T = Column(Float, nullable=False)  # Transmisión
    D = Column(Float, nullable=False)  # Distribución
    R = Column(Float, nullable=False)  # Operación Red
    C = Column(Float, nullable=False)  # Comercialización
    P = Column(Float, nullable=False)  # Pérdidas
    
    # Costo Unitario Total
    CU = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<Tariff(id_market={self.id_market}, voltage_level={self.voltage_level}, cdi={self.cdi}, CU={self.CU})>"


class Service(Base):
    """Maestro de Puntos de Servicio
    
    Identifica a usuarios (clientes) y sus condiciones de conexión.
    FK compuesta hacia tariffs: (id_market, voltage_level, cdi).
    """
    __tablename__ = 'services'
    
    id_service = Column(Integer, primary_key=True)
    id_market = Column(Integer, ForeignKey('tariffs.id_market'), nullable=False)
    voltage_level = Column(Integer, ForeignKey('tariffs.voltage_level'), nullable=False)
    cdi = Column(Integer, ForeignKey('tariffs.cdi'), nullable=True)
    
    # Relación con records
    records = relationship('Record', back_populates='service')
    
    def __repr__(self):
        return f"<Service(id_service={self.id_service}, id_market={self.id_market}, voltage_level={self.voltage_level}, cdi={self.cdi})>"


class Record(Base):
    """Índice de Tiempo / Tabla Pivote
    
    Centraliza marcas de tiempo para cada servicio.
    Relación 1:N con services; N:1 con consumption e injection.
    """
    __tablename__ = 'records'
    
    id_record = Column(Integer, primary_key=True)
    id_service = Column(Integer, ForeignKey('services.id_service'), nullable=False)
    record_timestamp = Column(DateTime, nullable=False)
    
    # Relaciones
    service = relationship('Service', back_populates='records')
    consumption = relationship('Consumption', back_populates='record', uselist=False)
    injection = relationship('Injection', back_populates='record', uselist=False)
    
    def __repr__(self):
        return f"<Record(id_record={self.id_record}, id_service={self.id_service}, timestamp={self.record_timestamp})>"


class Consumption(Base):
    """Medición de Consumo
    
    Almacena energía activa consumida (kWh).
    Relación 1:1 con records.
    """
    __tablename__ = 'consumption'
    
    id_record = Column(Integer, ForeignKey('records.id_record'), primary_key=True)
    value = Column(Float, nullable=False)
    
    # Relación
    record = relationship('Record', back_populates='consumption')
    
    def __repr__(self):
        return f"<Consumption(id_record={self.id_record}, value={self.value} kWh)>"


class Injection(Base):
    """Medición de Inyección
    
    Almacena energía exportada a la red (kWh).
    Relación 1:1 con records.
    """
    __tablename__ = 'injection'
    
    id_record = Column(Integer, ForeignKey('records.id_record'), primary_key=True)
    value = Column(Float, nullable=False)
    
    # Relación
    record = relationship('Record', back_populates='injection')
    
    def __repr__(self):
        return f"<Injection(id_record={self.id_record}, value={self.value} kWh)>"


class XmData(Base):
    """Precios de Bolsa Horarios
    
    Almacena precios de energía de bolsa (XM) por hora.
    Lookup table para cálculo de EE2.
    """
    __tablename__ = 'xm_data'
    
    record_timestamp = Column(DateTime, primary_key=True)
    value = Column(Float, nullable=False)
    
    def __repr__(self):
        return f"<XmData(timestamp={self.record_timestamp}, price={self.value} COP/kWh)>"


# Crear engine y base de datos
def init_db(db_path='facturacion.db'):
    """Inicializa la base de datos SQLite con todas las tablas."""
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    print(f"✓ Base de datos inicializada en {db_path}")
    return engine


if __name__ == '__main__':
    engine = init_db()
    print("✓ Estructura de base de datos creada exitosamente.")

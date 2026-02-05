from sqlalchemy import Column, String, Integer, DateTime, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class EtlRun(Base):
    __tablename__ = "etl_run"

    run_id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    current_phase = Column(String, nullable=False)
    error_message = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class EtlCheckpoint(Base):
    __tablename__ = "etl_checkpoint"

    run_id = Column(String, primary_key=True)
    phase = Column(String, primary_key=True)
    cursor = Column(String, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

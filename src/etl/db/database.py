from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from etl.config.settings import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

# Create session factory
Session = sessionmaker(bind=engine)

# Create tables
# Base.metadata.create_all(engine)

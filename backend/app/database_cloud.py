# Updated database configuration for cloud deployment
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import event
from sqlalchemy.pool import Pool
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# PostgreSQL async connection
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:password@localhost:5432/rubiscape_ml"
)

# Cloud SQL specific configuration
POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "20"))
MAX_OVERFLOW = int(os.getenv("DB_POOL_MAX_OVERFLOW", "0"))
POOL_RECYCLE = 3600  # Recycle connections every hour
POOL_PRE_PING = True  # Enable pre-ping to detect stale connections

engine = create_async_engine(
    DATABASE_URL,
    echo=os.getenv("DB_ECHO", "false").lower() == "true",
    future=True,
    pool_pre_ping=POOL_PRE_PING,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_recycle=POOL_RECYCLE,
    echo_pool=True,  # Log pool operations
    connect_args={
        "server_settings": {
            "jit": "off",  # Disable JIT for better performance on Cloud SQL
            "max_parallel_workers_per_gather": "4",
        },
        "timeout": 30,  # Connection timeout
    }
)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
)

Base = declarative_base()

async def get_db():
    """Dependency for getting database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

# Event listeners for connection pooling
@event.listens_for(Pool, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Called when a connection is created"""
    logger.debug(f"New database connection established")

@event.listens_for(Pool, "close")
def receive_close(dbapi_conn, connection_record):
    """Called when a connection is returned to the pool"""
    logger.debug(f"Connection returned to pool")

@event.listens_for(Pool, "detach")
def receive_detach(dbapi_conn, connection_record):
    """Called when a connection is detached"""
    logger.debug(f"Connection detached")

@event.listens_for(Pool, "checkout")
def receive_checkout(dbapi_conn, connection_record, connection_proxy):
    """Called when a connection is checked out from the pool"""
    logger.debug(f"Connection checked out from pool")

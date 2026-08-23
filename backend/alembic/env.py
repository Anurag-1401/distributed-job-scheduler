import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import async_engine_from_config

from app import models  # noqa: F401
from app.core.config import get_settings
from app.db import Base

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
target_metadata = Base.metadata

settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.normalized_database_url)


def run_migrations_offline():
    context.configure(url=settings.normalized_database_url, target_metadata=target_metadata, literal_binds=True, dialect_opts={"paramstyle": "named"})
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    connectable = async_engine_from_config(config.get_section(config.config_ini_section), prefix="sqlalchemy.", poolclass=None)
    async with connectable.connect() as connection:
        await connection.run_sync(lambda sync_conn: context.configure(connection=sync_conn, target_metadata=target_metadata))
        await connection.run_sync(lambda sync_conn: _run(sync_conn))
    await connectable.dispose()


def _run(connection):
    with context.begin_transaction():
        context.configure(connection=connection, target_metadata=target_metadata)
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())

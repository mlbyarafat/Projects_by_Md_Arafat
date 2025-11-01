from logging.config import fileConfig
import os
from sqlalchemy import engine_from_config, pool
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

fileConfig(config.config_file_name)

# add your model's MetaData object here for 'autogenerate' support
# for example: from myapp import models; target_metadata = models.Base.metadata
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from database import Base
try:
    target_metadata = Base.metadata
except Exception:
    target_metadata = None

def run_migrations_offline():
    url = os.getenv('DATABASE_URL', config.get_main_option('sqlalchemy.url'))
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='',
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

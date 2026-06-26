from alembic.config import Config
from sqlalchemy import inspect

from alembic import command
from app.db import engine


def run_migrations() -> None:
    config = Config("alembic.ini")
    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    if "groups" in tables and "alembic_version" in tables:
        with engine.connect() as connection:
            sql = "SELECT version_num FROM alembic_version"
            current = connection.exec_driver_sql(sql).fetchall()
        if not current:
            command.stamp(config, "0001_initial")
    command.upgrade(config, "head")

import os

import psycopg2

# TODO actual configuration
config = {
    "database.bareflow.host": os.getenv("POSTGRES_HOST", "localhost"),
    "database.bareflow.port": 5432,
    "database.bareflow.username": "postgres",
    "database.bareflow.password": "postgres",
    "database.bareflow.database": "postgres",
    "database.bareflow.ssl_mode": "disable",
}


def get_connection_for(db_name: str) -> psycopg2.extensions.connection:
    host = config.get(f"database.{db_name}.host", "localhost")
    port = config.get(f"database.{db_name}.port", 5432)
    user = config.get(f"database.{db_name}.username", None)
    password = config.get(f"database.{db_name}.password", "")
    database = config.get(f"database.{db_name}.database", None)
    ssl_mode = config.get(f"database.{db_name}.ssl_mode", None)
    return psycopg2.connect(f"postgresql://{user}:{password}@{host}:{port}/{database}", sslmode=ssl_mode)


def get_autocommit_conn_for(db_name):
    conn = get_connection_for(db_name)
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


drop_tables = [
    "drop table if exists flow_runs cascade;",
    "drop table if exists flow_run_steps;"
]

tables = [
    """
    create table if not exists flow_runs (
        id int generated always as identity,
        flow_id text not null,
        outcome text,
        stats jsonb,
        created_at timestamp not null default now(),
        updated_at timestamp not null default now(),

        PRIMARY KEY(id)
    )
    """,
    """
    create table if not exists flow_run_steps (
        id int generated always as identity,
        flow_run_id int,
        name text,
        image text,
        pod_name text,
        log_status text,
        command text[],
        depends_on text[],
        status text,
        created_at timestamp not null default now(),
        updated_at timestamp not null default now(),
        started_at timestamp,
        ended_at timestamp,

        constraint fk_flow_run
            foreign key(flow_run_id)
                references  flow_runs(id)
    )
    """,
]


def setup_tables(force:bool=False) -> None:
    with get_connection_for("bareflow") as conn:
        with conn.cursor() as cur:
            if force:
                for statement in drop_tables:
                    cur.execute(statement)
            for create_statement in tables:
                cur.execute(create_statement)
        conn.commit()


if __name__ == "__main__":
    # As a convenience when this file is run directly
    # the database is totally reset.
    setup_tables(True)

from typing import List
from .setup import get_connection_for
import psycopg2.extras
from psycopg2.extras import RealDictCursor as rd


def get_flows():
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            cur.execute(
                """
            select * from flows
            """
            )
            return cur.fetchall()


def insert_flow(flow_id: str):
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            cur.execute(
                """
            insert into flows (id, enabled) values (%s, false)
            """,
                (flow_id,),
            )


def delete_flow_by_id(flow_id: str):
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            cur.execute(
                """
            delete from flows where id = %s
            """,
                (flow_id,),
            )


def create_flow_run_and_steps(flow_id: str, steps: List[dict]) -> dict:
    with get_connection_for("bareflow") as conn:
        with conn.cursor() as cur:
            # Can't use realdictcursor with execute_values :(
            cur.execute("insert into flow_runs (flow_id) values (%s) returning id", [flow_id])
            flow_run_id = cur.fetchone()

            values = list(map(lambda step: (flow_run_id, step["name"], step["image"], step["command"],), steps,))
            insert_query = """
                insert into flow_run_steps (flow_run_id, name, image, command)
                values %s
                """

            psycopg2.extras.execute_values(cur, insert_query, values, template=None, page_size=100)

    return get_flow_run(flow_run_id)


def update_flow_run_step(flow_run_step_id: int, **kwargs) -> dict:
    values = ",".join([f"{key} = '{value}'" for key, value in kwargs.items()])
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            q = f"""
            update flow_run_steps
            set {values}
            where id = %s
            """
            cur.execute(q, [flow_run_step_id])

    return get_flow_run_step(flow_run_step_id)


def get_flow_run(flow_run_id: int, **kwargs) -> dict:
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            q = f"""
            select * from
            flow_runs
            left join flow_run_steps
                on flow_runs.id = flow_run_steps.flow_run_id
            where flow_runs.id = %s
            """
            cur.execute(q, (flow_run_id,))
            return cur.fetchall()


def get_flow_run_step(flow_run_step_id: int) -> dict:
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            q = f"""
            select
                flow_run_steps.id as id,
                flow_runs.flow_id,
                flow_runs.id as flow_run_id,
                flow_runs.outcome as flow_run_outcome,
                flow_run_steps.image,
                flow_run_steps.pod_name,
                flow_run_steps.name,
                flow_run_steps.command,
                flow_run_steps.depends_on,
                flow_run_steps.status,
                flow_run_steps.started_at,
                flow_run_steps.ended_at
            from flow_runs
            left join flow_run_steps
                on flow_runs.id = flow_run_steps.flow_run_id
            where flow_run_steps.id = %s
            """
            cur.execute(q, [flow_run_step_id])
            return dict(cur.fetchall()[0])


def get_steps_for_n_flow_runs(limit: int) -> dict:
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            q = f"""
                with ranked as (
                    select flow_id, id, row_number() over (partition by flow_id order by id desc) as rk
                    from flow_runs
                )
                select
                    flow_run_steps.id,
                    flow_runs.flow_id,
                    flow_runs.id as flow_run_id,
                    flow_runs.outcome as flow_run_outcome,
                    flow_run_steps.image,
                    flow_run_steps.pod_name,
                    flow_run_steps.name,
                    flow_run_steps.command,
                    flow_run_steps.depends_on,
                    flow_run_steps.status,
                    flow_run_steps.started_at,
                    flow_run_steps.ended_at
                from flow_runs
                left join flow_run_steps
                    on flow_runs.id = flow_run_steps.flow_run_id
                where flow_runs.id in (select id from ranked where rk <= {limit})
            """
            cur.execute(q)
            return cur.fetchall()


def get_unscheduled_flow_run_steps():
    # used by the scheduler to determine at each time step
    # which flow steps to start up
    with get_connection_for("bareflow") as conn:
        with conn.cursor(cursor_factory=rd) as cur:
            q = f"""
            with exploded as (
                select
                    id,
                    flow_run_id,
                    array_length(depends_on, 1) as num_deps,
                    unnest(depends_on) as dep_name
                from flow_run_steps
                where status not in ('succeeded', 'failed', 'skipped')
            ),
            met_dependencies as (
                select
                    distinct exploded.id
                from exploded
                left join flow_run_steps deps
                    on exploded.dep_name = deps.name
                    and exploded.flow_run_id = deps.flow_run_id
                where
                    num_deps is null or num_deps = 0 or deps.status in ('succeeded')
            )
                select
                    flow_run_steps.id as id,
                    flow_runs.flow_id,
                    flow_runs.id as flow_run_id,
                    flow_runs.outcome as flow_run_outcome,
                    flow_run_steps.image,
                    flow_run_steps.pod_name,
                    flow_run_steps.name,
                    flow_run_steps.command,
                    flow_run_steps.depends_on,
                    flow_run_steps.status,
                    flow_run_steps.started_at,
                    flow_run_steps.ended_at
                from flow_runs
                inner join flow_run_steps
                    on flow_runs.id = flow_run_steps.flow_run_id
                left join met_dependencies
                    on flow_run_steps.id = met_dependencies.id
                where (met_dependencies.id is not null or depends_on is null)
                    and status is null
            """
            cur.execute(q)
            return cur.fetchall()

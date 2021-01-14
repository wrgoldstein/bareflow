from lib.database import get_connection_for

with get_connection_for("bareflow") as conn:
    with conn.cursor() as cur:
        flow_id = "apple"
        cur.execute("insert into flow_runs (flow_id) values (%s) returning id", [flow_id])
        print(cur.fetchone())

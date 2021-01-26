
from lib.flow import step

step(
    flow_id="count-to-30",
    name="counting",  # no underscores
    image="counterimage",
    command=["/app/counter.sh"],
    schedule="*/3 * * * *"
)

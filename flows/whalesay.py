from lib.flow import step

step(
    flow_id="whalesay",
    name="whalesay",  # no underscores
    image="docker/whalesay",
    command=["cowsay", "better mortgage so fun"],
    # schedule="0 */2 * * *"
)

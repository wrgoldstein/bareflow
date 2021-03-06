from lib.flow import step

step(
    flow_id="cowsaytwice",
    name="whalesay",  # no underscores
    image="docker/whalesay",
    command=["cowsay", "better mortgage so fun"]
    # schedule="0 */2 * * *"
)

step(
    flow_id="cowsaytwice",
    name="always-fail",
    image="bash",
    command=["false"],
    depends_on=["whalesay"]
)

step(
    flow_id="cowsaytwice",
    name="whalesay-again",  # no underscores
    image="docker/whalesay",
    command=["cowsay", "oh gosh number two"],
    depends_on=["whalesay", "always-fail"]
    # schedule="0 */2 * * *"
)

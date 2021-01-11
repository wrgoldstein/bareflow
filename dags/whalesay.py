from flow import job

job(
    name="whalesay",  # no underscores
    image="docker/whalesay",
    command=["cowsay", "better mortgage so fun"],
    schedule="0 */2 * * *"
)

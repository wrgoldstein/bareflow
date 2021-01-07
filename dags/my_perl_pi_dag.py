from flow import job

job(
    name="my-perl-pi-dag",  # no underscores
    image="perl",
    command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
    schedule="5 4 * * *"
)

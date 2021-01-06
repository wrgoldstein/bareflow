from flow import job

job(
    name="my_perl_pi_dag",
    image="perl",
    command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
    schedule="5 4 * * *"
)

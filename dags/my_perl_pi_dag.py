def job():
    return dict(
        image="perl",
        command=["perl", "-Mbignum=bpi", "-wle", "print bpi(2000)"],
    )

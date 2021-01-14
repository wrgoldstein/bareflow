"""
this flow prints the first few digits of pi, twice.
"""

from lib.flow import step

step(
    flow_id="pi-flow",
    name="pi-print-one",
    image="perl",
    command=["perl", "-Mbignum=bpi", "-wle", "print bpi(100)"],
)

step(
    flow_id="pi-flow",
    name="pi-print-two",
    image="perl",
    command=["perl", "-Mbignum=bpi", "-wle", "print bpi(50)"],
)

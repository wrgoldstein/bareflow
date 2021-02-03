
# from lib.flow import step

# @step
# def counting():
#     pass

# with flow('count-to-30'):
#     schedule('*/3 * * * *')

#     counting = step(
#         name="counting",
#         image="counterimage",
#         command=["/app/counter.sh"],
#     )

#     say_done = step(
#         name="say-done",
#         image="docker/whalesay",
#         command=["cowsay", "done!"],
#     )

#     with alpha():
#         with beta():
#             gamma()
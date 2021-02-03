# from bearflow import flow, step, trigger

# def trigger_beta(steps):
#   pass

# with flow('my-flow'):
#   step('alpha', image='doodoo', command=['poopoo'])

# #   with trigger('alpha', run_if = lambda x: x['alpha'].state == 'succeeded' )
# #     step('beta', image='doodoo', command=['dsada'])

#     with succeeded('alpha'), succeeded('beta'):
#         gamma = step('gamma', image='dsada')
#         with succeeded(gamma):
#             step('final_step', image='dsadas')

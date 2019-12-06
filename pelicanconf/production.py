import os

with open(os.path.join(os.path.dirname(__file__), 'base.py')) as mod:
    exec(mod.read())

GOOGLE_ANALYTICS = 'UA-46117138-1'

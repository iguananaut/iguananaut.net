import os

with open(os.path.join(os.path.dirname(__file__), 'base.py')) as mod:
    exec(mod.read())

RELATIVE_URLS = True

import logging


def enable_std_output():
    root = logging.getLogger()
    root.setLevel(logging.INFO)

import logging
import sys

from golem_remote.consts import LOGGER_NAME


def enable_std_output():
    root = logging.getLogger(LOGGER_NAME)
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

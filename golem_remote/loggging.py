import logging
import sys

from golem_remote.consts import LOGGER_NAME


def enable_std_output():
    # logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

    root = logging.getLogger()
    root.setLevel(logging.INFO)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s\t:\t%(name)s\t\t%(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)

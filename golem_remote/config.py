from pathlib import Path

from golem_remote.runf_helpers import Host, Port

PYTHON_PATH = Path("/", "home", "jacek", "golemenv", "bin", "python3")
GOLEM_DIR = Path("/", "home", "jacek", "golem_data", "golem4_r")
GOLEMCLI = Path("/", "home", "jacek", "golem_orig", "golemcli.py")

GOLEM_PORT: Port = 40102
GOLEM_HOST: Host = "127.0.0.1"

QUEUE_PORT: Port = 6379
QUEUE_HOST: Host = "127.0.0.1"

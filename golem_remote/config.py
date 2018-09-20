from pathlib import Path

from golem_remote.runf_helpers import Host, Port

PYTHON_PATH = Path("~", "golemenv", "bin", "python3").expanduser()
GOLEM_DIR = Path("~", "golem_data", "golem4_r").expanduser()
GOLEMCLI = Path("~", "golem_orig", "golemcli.py").expanduser()

GOLEM_PORT: Port = 40102
GOLEM_HOST: Host = "127.0.0.1"

QUEUE_PORT: Port = 6379
QUEUE_HOST: Host = "127.0.0.1"

from functools import wraps
from pathlib import Path

from golem_remote.runf_helpers import Host, Port
from .golem_client import GolemClientInterface, GolemClient

__all__ = ["init", "remote", "get"]


client: GolemClientInterface = None


class RemoteFunction():
    def __init__(self, f, client: GolemClientInterface):
        self.f = f
        self.client = client

    # TODO should have the same signature as f
    # but for now we'll leave it like this
    def remote(self, *args, **kwargs):
        subtask_id = client.run_function(self.f, args, kwargs)
        return subtask_id


def golem_running(f):
    @wraps(f)
    def checked(*args, **kwargs):
        global client
        if not client:
            raise Exception("You forgot to golem.init()")
        return f(*args, **kwargs)
    return checked


@golem_running
def remote(f):
    return RemoteFunction(f, client)


@golem_running
def get(subtask_id):
    global client
    return client.get(subtask_id)


def init(host: Host="127.0.0.1",
         port: Port=61000,
         golem_dir: Path=Path("/home/jacek/golem_data/golem4_r"),
         golemcli: Path=Path("/home/jacek/golem_orig/golemcli.py"),
         class_=GolemClient,
         blocking=True,
         timeout=30):
    global client
    client = class_(golem_host=host,
                    golem_port=port,
                    golem_dir=golem_dir,
                    golemcli=golemcli,
                    tempdir=Path("./temp/"),
                    blocking=blocking,
                    timeout=timeout)
    client.initialize_task()

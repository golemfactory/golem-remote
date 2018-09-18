from functools import wraps
from pathlib import Path
from typing import Optional, Set

from golem_remote import config
from golem_remote.logging import enable_std_output
from golem_remote.runf_helpers import Host, Port, TaskID, SubtaskParams, SubtaskData
from .golem_client import GolemClientInterface, GolemClient

client: Optional[GolemClientInterface] = None  # pylint: disable=global-statement

enable_std_output()


class RemoteFunction():
    # pylint: disable=redefined-outer-name
    def __init__(self, function, client: GolemClientInterface) -> None:
        self.function = function
        self.client = client

    # TODO should have the same signature as f
    # but for now we'll leave it like this
    def remote(self, *args, **kwargs):
        subtask_id = client.run_function(
            SubtaskData(
                function=self.function,
                args=args,
                kwargs=kwargs,
                params=SubtaskParams(original_dir=Path(".").absolute())
            )
        )
        return subtask_id


def golem_running(f):
    @wraps(f)
    def checked(*args, **kwargs):
        global client  # pylint: disable=global-statement
        if not client:
            raise Exception("You forgot to golem.init()")
        return f(*args, **kwargs)

    return checked


@golem_running
def remote(f):
    return RemoteFunction(f, client)


@golem_running
def get(subtask_id):
    global client  # pylint: disable=global-statement
    return client.get(subtask_id)


def init(host: Host = "127.0.0.1",
         port: Port = 61000,
         golem_dir: Path = config.GOLEM_DIR,
         golemcli: Path = config.GOLEMCLI,
         class_=GolemClient,
         blocking=True,
         timeout=30,
         number_of_subtasks: int = 1,
         clear_db: bool = False,
         task_id: TaskID = None,
         task_files: Optional[Set[Path]] = None) -> TaskID:
    global client  # pylint: disable=global-statement
    client = class_(
        golem_host=host,
        golem_port=port,
        golem_dir=golem_dir,
        golemcli=golemcli,
        blocking=blocking,
        timeout=timeout,
        number_of_subtasks=number_of_subtasks,
        clear_db=clear_db,
        task_id=task_id,
        task_files=task_files)
    client.initialize_task()  # type: ignore
    return client.task_id  # type: ignore

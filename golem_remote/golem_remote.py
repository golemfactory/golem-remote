import logging
from functools import wraps
from pathlib import Path
from typing import Optional, Set, Union, Iterable, Any, Callable, List

from golem_remote import config
from golem_remote.runf_helpers import Host, Port, TaskID, SubtaskParams, SubtaskData, SubtaskID
from .golem_client import GolemClientInterface, GolemClient

# Between singleton and global var, I choose global var
client: Optional[GolemClientInterface] = None  # pylint: disable=global-statement

# Enable INFO logging - just for debugging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RemoteFunction():
    # pylint: disable=redefined-outer-name
    def __init__(self, function: Callable[..., Any], client: GolemClientInterface) -> None:
        self.function = function
        self.client = client

    # TODO remote should have the same signature as f - use functools.wraps or inspect module
    def remote(self, *args, **kwargs) -> SubtaskID:
        subtask_id = self.client.run_function(
            SubtaskData(
                function=self.function,
                args=args,
                kwargs=kwargs,
                params=SubtaskParams(original_dir=Path(".").absolute())))
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


# @golem_running
# def wait(items: Iterable[SubtaskID], num_returns=1):
#     """This waits for the k of n promises to resolve analogously to ray.wait() - e.g. if
#         f(x) = sleep(x); return x
#         Fx = f.remote(x)
#     then
#         golem.get([F1, F4, F5, F3], 2) == ([1, 3], [F4, F5])"""
#     raise NotImplementedError()


@golem_running
def get(item: Union[SubtaskID, Iterable[SubtaskID]]) -> Union[Any, List[Any]]:
    """Wait for the promise(s) to resolve and return corresponding object(s)"""
    global client  # pylint: disable=global-statement

    if isinstance(item, SubtaskID):
        return client.get(item)

    if isinstance(item, Iterable):
        # for x in item:
        #     yield client.get(x)
        return [client.get(x) for x in item]

    raise Exception(f"Non supported parameter: got type {type(item)}, "
                    f"should be {Union[SubtaskID, Iterable[SubtaskID]]}")


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
    client.initialize_task()
    return client.task_id  # type: ignore

from pathlib import Path
from typing import NamedTuple, List, Dict, Callable, Any, Tuple

SubtaskID = str
QueueID = str
TaskID = str

Host = str
Port = int


# meta-parameters for golem
class SubtaskParams(NamedTuple):
    # the base directory that paths should be expanded relative to
    # e.g. if in the function user reads ("./aa/bb"), then golem has to know
    # how to expand ".".
    original_dir: Path


# TODO should be typed differently
class SubtaskData(NamedTuple):
    args: Tuple[...]
    kwargs: Dict[str, Any]
    function: Callable[..., Any]
    params: SubtaskParams



class SubtaskDefinition(NamedTuple):
    subtask_id: SubtaskID
    queue_id: QueueID
    data: SubtaskData


class FinishComputations(NamedTuple):
    pass

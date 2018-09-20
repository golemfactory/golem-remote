from pathlib import Path
from typing import NamedTuple, Dict, Callable, Any, Tuple

SubtaskID = str
QueueID = str
TaskID = str

Host = str
Port = int


class SubtaskParams(NamedTuple):
    """Meta-parameters for Golem"""

    # the base directory that paths should be expanded relative to
    # e.g. if in the function user reads ("./aa/bb"), then golem has to know
    # how to expand ".".
    original_dir: Path


# TODO should be typed differently, but it is not possible with current mypy
class SubtaskData(NamedTuple):
    args: Tuple[Any, ...]
    kwargs: Dict[str, Any]
    function: Callable[..., Any]
    params: SubtaskParams


class SubtaskDefinition(NamedTuple):
    subtask_id: SubtaskID
    queue_id: QueueID
    data: SubtaskData


class FinishComputations(NamedTuple):
    pass

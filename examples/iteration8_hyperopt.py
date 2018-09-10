from typing import List

from hyperopt import fmin, tpe, hp

import golem_remote.golem_remote as golem
from golem_remote import GolemClient

N = 10

class Poly:
    def __init__(self, l: List[float]=None):
        if l is None:
            self.l = []
        else:
            self.l = l

    def evaluate(self, point: float):
        value = 0
        for w in self.l:
            value = value * point + w
        return value


golem.init(
    class_=GolemClient,
    timeout=300,
    number_of_subtasks=N
)


@golem.remote
def fn(x: float):
    return Poly([2,-4,3,1,0,2]).evaluate(x)


best = fmin(
    fn=lambda x: golem.get(fn.remote(x)),
    space=hp.uniform('x', -10, 10),
    algo=tpe.suggest,
    max_evals=N,
    verbose=1
)


print(f"Result: {best}")

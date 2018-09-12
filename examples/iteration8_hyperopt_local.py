from hyperopt import fmin, tpe, hp

N = 30


def fn(x: float):
    from typing import List

    class Poly:
        def __init__(self, l: List[float] = None):
            if l is None:
                self.l = []
            else:
                self.l = l

        def evaluate(self, point: float):
            value = 0
            for w in self.l:
                value = value * point + w
            return value

    return Poly([4,-3,-1,0,2]).evaluate(x)


best = fmin(
    fn=lambda x: fn(x),
    space=hp.uniform('x', -2, 2),
    algo=tpe.suggest,
    max_evals=N,
    verbose=1,
    max_queue_len=N//2
)


print(f"Result: {best}")

from hyperopt import fmin, tpe, hp
from hyperopt.mongoexp import MongoTrials

trials = MongoTrials('mongo://localhost:27017/foo_db/jobs', exp_key='exp1')

N = 30


def fn(x: float):
    from typing import List
    import time
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

    print("sleeping...")
    time.sleep(10)
    print("woke up!")
    return Poly([4,-3,-1,0,2]).evaluate(x)


best = fmin(
    fn=fn,
    space=hp.uniform('x', -2, 2),
    algo=tpe.suggest,
    max_evals=N,
    verbose=1,
    max_queue_len=N//2,
    trials=trials
)


print(f"Result: {best}")

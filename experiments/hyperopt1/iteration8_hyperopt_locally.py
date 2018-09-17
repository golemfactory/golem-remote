import os
import signal
import subprocess
from threading import Thread
from uuid import uuid4

import hyperopt
from hyperopt import fmin, hp
from hyperopt.mongoexp import MongoTrials

trials = MongoTrials('mongo://localhost:27017/foo_db/jobs', exp_key=str(uuid4()))

N = 100
NUM_WORKERS = 3


# golem.init(
#     class_=GolemClient,
#     timeout=3000,
#     number_of_subtasks=N,
#     clear_db=True
# )


# @golem.remote
def fn(x: float):
    # from typing import List
    # class Poly:
    #     def __init__(self, l: List[float] = None):
    #         if l is None:
    #             self.l = []
    #         else:
    #             self.l = l
    #
    #     def evaluate(self, point: float):
    #         value = 0
    #         for w in self.l:
    #             value = value * point + w
    #         return value
    # return Poly([2,-4,3,1,0,2]).evaluate(x)
    return (x - 3) * (x - 2) * (x - 1) * x * (x + 1) * (x + 2) * (x + 3)


RETURN_VALUE = []
THREADS = []


def spawn_head():
    r = fmin(
        fn=fn,  # lambda x: golem.get(fn.remote(x)),
        space=hp.uniform('x', -3, 3),
        algo=hyperopt.rand.suggest,
        max_evals=N,
        verbose=1,
        max_queue_len=N,
        trials=trials
    )
    RETURN_VALUE.append(r)


def spawn_worker():
    p = subprocess.Popen(["hyperopt-mongo-worker",
                          "--mongo=localhost:27017/foo_db",
                          "--poll-interval=0.1"])
    print("abcd")
    THREADS.append(p.pid)


head_thread = Thread(target=spawn_head)
head_thread.start()
print("spawned head")

os.setpgrp()

threads = []
for e in range(NUM_WORKERS):
    spawn_worker()

print("waiting")
head_thread.join()

print(f"THREADS: {THREADS}")

for t in THREADS:
    print(f"Killing {t}")
    os.kill(t, signal.SIGKILL)

for t in threads:
    t.terminate()

print(f"Result: {RETURN_VALUE}")

os.killpg(0, signal.SIGKILL)

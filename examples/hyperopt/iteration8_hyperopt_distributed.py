import os
import signal
import subprocess
from threading import Thread

from uuid import uuid4

import hyperopt
from hyperopt import fmin, hp
from hyperopt.mongoexp import MongoTrials
import golem_remote as golem

trials = MongoTrials('mongo://localhost:27017/foo_db/jobs', exp_key=str(uuid4()))

N = 2
NUM_WORKERS = 2

params = dict(
    class_=golem.GolemClient,
    timeout=3000,
    number_of_subtasks=N,
    clear_db=False
)

TASK_ID = golem.init(**params)

with open("/home/jacek/temp.id", "w") as f:
    f.write(TASK_ID)

def fn(x: float):
    with open("/home/jacek/tempid", "r") as f:
        TASK_ID = f.read()

    golem.init(**{"task_id": TASK_ID, **params})
    @golem.remote
    def f(x):
        return (x - 3) * (x - 2) * (x - 1) * x * (x + 1) * (x + 2) * (x + 3)

    return golem.get(f.remote(x))


RETURN_VALUE = []
THREADS = []

def spawn_head():
    r = fmin(
        fn=fn,
        space=hp.uniform('x', -3, 3),
        algo=hyperopt.rand.suggest,
        max_evals=N,
        verbose=1,
        max_queue_len=N,
        trials=trials
    )
    RETURN_VALUE.append(r)


def spawn_worker():
    p = subprocess.Popen(["/home/jacek/anaconda3/bin/hyperopt-mongo-worker",
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

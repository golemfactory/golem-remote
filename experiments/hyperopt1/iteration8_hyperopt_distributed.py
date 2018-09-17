import json
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

N = 50
NUM_WORKERS = 4

params = dict(
    class_=golem.GolemClient,
    timeout=3000,
    number_of_subtasks=N,
    clear_db=False
)

TASK_ID = golem.init(**params)

with open("/home/jacek/temp.id", "w") as f:  # for some reason, hyperopt doesn't serialize closures
    f.write(TASK_ID)

def fn(x: float):
    with open("/home/jacek/temp.id", "r") as f:
        TASK_ID = f.read()

    golem.init(**{"task_id": TASK_ID, **params})
    @golem.remote
    def f(x):
        return (x - 3) * (x - 2) * (x - 1) * x * (x + 1) * (x + 2) * (x + 3)

    return golem.get(f.remote(x))


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
    with open("res.json", "w") as f:
        json.dump(r, f)


def spawn_worker():
    subprocess.Popen(["/home/jacek/anaconda3/bin/hyperopt-mongo-worker",
                          "--mongo=localhost:27017/foo_db",
                          "--poll-interval=0.1"])


head_thread = Thread(target=spawn_head)
head_thread.start()
print("Spawned head")

os.setpgrp()

for e in range(NUM_WORKERS):
    spawn_worker()

print("Waiting")
head_thread.join()

os.killpg(0, signal.SIGKILL)

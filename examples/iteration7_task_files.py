import os
import shutil
import time
from pathlib import Path
from typing import Tuple

import golem_remote.golem_remote as golem
from golem_remote import GolemClient
from golem_remote.runf_helpers import SubtaskID

##############
# golem init #
##############

shutil.rmtree("abcd", ignore_errors=True)
os.mkdir("abcd")
with open("./abcd/aaa.txt", "w") as f:
    f.write("Wstąpiłem na działo")


golem.init(
    class_=GolemClient,
    timeout=300,
    task_files={Path("./abcd/aaa.txt")}
)

#######################
# function definition #
#######################

secret_sauce = "Secret"


@golem.remote
def func(arg1: int, arg2: int, kwarg1: str="abc", kwarg2: str="def") -> Tuple[int, str, str, str]:
    time.sleep(1)  # expensive call
    with open("./abcd/aaa.txt", "r") as f:
        c = f.read()

    print(f"Running func: {arg1} {arg2} {kwarg1} {kwarg2} {c}")
    return (arg1 + arg2, kwarg1 + kwarg2, secret_sauce, c)


##################
# function calls #
##################

res_id1: SubtaskID = func.remote(1, 2, kwarg1="abcd")

res1 = golem.get(res_id1)
print(f"Result: {res1}")

assert res1 == (1 + 2, "abcd" + "def", secret_sauce, "Wstąpiłem na działo")
print("Assert: True")

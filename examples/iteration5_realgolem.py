from pathlib import Path

import golem_remote.golem_remote as golem
from golem_remote.runf_helpers import SubtaskID, Host, Port
from golem_remote.golem_client import GolemClient

from typing import Tuple
import time

# although I will use golemcli at the beginning
# because doing anything with WAMP is so painful
host: Host = "127.0.0.1"
port: Port = 61000
golem_dir = Path("/home/jacek/golem_data/golem5_r")
golemcli = Path("/home/jacek/golem_orig/golemcli.py")


##############
# golem init #
##############

golem.init(
    host=host,
    port=port,
    golem_dir=golem_dir,
    class_=GolemClient,
    timeout=300
)

#######################
# function definition #
#######################

secret_sauce = "Secret"

@golem.remote
def func(arg1: int, arg2: int, kwarg1: str="abc", kwarg2: str="def") \
        -> Tuple[int, str, str]:
    time.sleep(1)  # expensive call
    print(f"Running func: {arg1} {arg2} {kwarg1} {kwarg2}")
    return (arg1 + arg2, kwarg1 + kwarg2, secret_sauce)

##################
# function calls #
##################

res_id1: SubtaskID = func.remote(1, 2, kwarg1="abcd")

# SubtaskIDs work as in ray
res1 = golem.get(res_id1)
print(f"Result: {res1}")
assert res1 == (1 + 2, "abcd" + "def", secret_sauce)
print("Assert: True")
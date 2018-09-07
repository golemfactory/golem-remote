import golem_remote.golem_remote as golem
from golem_remote.runf_helpers import SubtaskID
from golem_remote.golem_client import GolemClientMock

from typing import Tuple
import time

# although I will use golemcli at the beginning
# because doing anything with WAMP is so painful
host = "127.0.0.1" 
port = "61000"
golem_dir = "/home/jacek/golem_data/golem4_r"
golemcli = "/home/jacek/golem_orig/golemcli.py"


##############
# golem init #
##############

golem.init(class_=GolemClientMock)

#######################
# function definition #
#######################

secret_sauce = "Secret"

@golem.remote
def func(arg1: int, arg2: int, kwarg1: str="abc", kwarg2: str="def") -> Tuple[int, str]:
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
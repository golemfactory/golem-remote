import base64
import cloudpickle as pickle
import json
from typing import Any
import codecs


def encode_obj_to_str(obj: Any):
    result = pickle.dumps(obj)    
    result = base64.b64encode(result)
    result = codecs.decode(result, "ascii")
    result = {"r": result}
    result = json.dumps(result)
    return result


def decode_str_to_obj(s: str):
    result = json.loads(s)
    result = result["r"]
    result = codecs.encode(result, "ascii")
    result = base64.b64decode(result)
    result = pickle.loads(result)
    return result


class A():
    def __init__(self, a):
        self.a = a

a = A({"abcd": None})

assert decode_str_to_obj(encode_obj_to_str(a)).a == {"abcd": None}
print("Assert: True")
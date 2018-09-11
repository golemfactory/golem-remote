import base64
import codecs
import json
from typing import Any

import cloudpickle as pickle


def encode_obj_to_str(obj: Any) -> str:
    result = pickle.dumps(obj)
    result = base64.b64encode(result)
    result = codecs.decode(result, "ascii")
    result = {"r": result}
    result = json.dumps(result)
    return result


def decode_str_to_obj(s: str) -> Any:
    result = json.loads(s)
    result = result["r"]
    result = codecs.encode(result, "ascii")
    result = base64.b64decode(result)
    result = pickle.loads(result)
    return result

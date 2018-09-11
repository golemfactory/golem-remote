import unittest

from golem_remote import decode_str_to_obj, encode_obj_to_str



# TODO there should be also test for speed and for size of the encoding
class TestEncodingDecoding(unittest.TestCase):
    def test_encode_decode(self):
        identity = lambda x: decode_str_to_obj(encode_obj_to_str(x))

        self.assertEqual(identity(123), 123)

        class A():
            def __init__(self, x):
                self.x = x

        a = A({"abcd": 2345})
        self.assertEqual(identity(a).x, a.x)
        self.assertIsNone(identity(None))

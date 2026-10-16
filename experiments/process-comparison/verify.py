"""Author-only controls, not candidate submissions. Stdlib only."""
import json
import threading
import unittest
from urllib.error import HTTPError
from urllib.request import Request, urlopen
from fixture import make_server


def probe(variant, case):
    with make_server(variant) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"

        def post(body):
            req = Request(base + '/orders', json.dumps(body).encode(),
                          {'Content-Type': 'application/json'})
            try:
                response = urlopen(req, timeout=2)
            except HTTPError as error:
                response = error
            with response:
                return response.status, json.load(response)
        try:
            if case == 'api-zero':
                assert post({'id': 'a', 'quantity': 0})[0] == 422
            elif case == 'api-bool':
                assert post({'id': 'a', 'quantity': True})[0] == 422
            else:
                assert post({'id': 'a', 'quantity': 2})[0] == 201
                assert post({'id': 'a', 'quantity': 3})[0] == 409
                with urlopen(base + '/orders/a', timeout=2) as response:
                    assert json.load(response) == {'id': 'a', 'quantity': 2}
        finally:
            server.shutdown()
            thread.join(timeout=2)


class Controls(unittest.TestCase):
    def test_clean(self):
        for case in ('api-zero', 'api-bool', 'api-duplicate'):
            with self.subTest(case=case):
                probe('clean', case)

    def test_mutants_killed(self):
        for case in ('api-zero', 'api-bool', 'api-duplicate'):
            with self.subTest(case=case), self.assertRaises(AssertionError):
                probe(case, case)


if __name__ == '__main__':
    unittest.main(verbosity=2)

"""Deterministic scheduler reproducing a timing-dependent test failure."""
import argparse

SCHEDULE = (1, 3, 2, 4)


class Job:
    def __init__(self, delay, broken=False):
        self.delay = delay
        self.tick = 0
        self.broken = broken

    def advance(self):
        self.tick += 1

    @property
    def result(self):
        if self.tick < self.delay:
            return None
        return 'wrong' if self.broken else 'saved'


def original_test(job):
    for _ in range(2):
        job.advance()
    assert job.result == 'saved'


def reference_test(job):
    for _ in range(5):
        if job.result is not None:
            break
        job.advance()
    assert job.result == 'saved'


def outcomes(test, broken=False):
    results = []
    for delay in SCHEDULE:
        try:
            test(Job(delay, broken))
        except AssertionError:
            results.append('FAIL')
        else:
            results.append('PASS')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--verify', action='store_true')
    args = parser.parse_args()
    print('original:', outcomes(original_test))
    if args.verify:
        assert outcomes(original_test) == ['PASS', 'FAIL', 'PASS', 'FAIL']
        assert outcomes(reference_test) == ['PASS'] * 4
        assert outcomes(reference_test, broken=True) == ['FAIL'] * 4
        print('reference: 4/4 PASS; broken product: 4/4 detected')

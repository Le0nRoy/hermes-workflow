"""Author-only controls for the synthetic timing-flake fixture."""
import unittest

from flaky import Job, SCHEDULE, original_test, reference_test


class NeverCompletes(Job):
    @property
    def result(self):
        return None


class Controls(unittest.TestCase):
    def test_original_is_schedule_dependent(self):
        results = []
        for delay in SCHEDULE:
            with self.subTest(delay=delay):
                try:
                    original_test(Job(delay))
                except AssertionError:
                    results.append('FAIL')
                else:
                    results.append('PASS')
        self.assertEqual(results, ['PASS', 'FAIL', 'PASS', 'FAIL'])

    def test_reference_clean_including_boundaries(self):
        for delay in (0, *SCHEDULE, 5):
            with self.subTest(delay=delay):
                reference_test(Job(delay))

    def test_reference_detects_broken_result(self):
        for delay in (0, *SCHEDULE, 5):
            with self.subTest(delay=delay):
                with self.assertRaises(AssertionError):
                    reference_test(Job(delay, broken=True))

    def test_reference_fails_finitely_when_never_complete(self):
        job = NeverCompletes(0)
        with self.assertRaises(AssertionError):
            reference_test(job)
        self.assertEqual(job.tick, 5)


if __name__ == '__main__':
    unittest.main(verbosity=2)

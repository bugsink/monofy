import unittest

from monofy.scripts.monofy import ParentProcess


class MonofyTestCase(unittest.TestCase):

    def test_arg_parsing(self):
        def _check(argv, expected_pre_start, expected_parallel):
            pre_start = ParentProcess.get_pre_start_command_args(argv)
            parallel = ParentProcess.get_parallel_command_args(argv)
            self.assertEqual(expected_pre_start, pre_start)
            self.assertEqual(expected_parallel, parallel)

        _check(
            # this cannot really happen in practice, because we guard for "we need some args". Regardless, we keep the
            # test here to show what the parser would do (even if that's a bit weird, i.e. calling a single non-command)
            ["monofy.py"],
            [],
            [[]],
        )

        _check(
            ["monofy.py", "a", "b"],
            [],
            [["a", "b"]],
        )

        _check(
            ["monofy.py", "a", "b", "|||", "c", "d", "|||", "e", "f"],
            [],
            [["a", "b"], ["c", "d"], ["e", "f"]],
        )

        _check(
            ["monofy.py", "a", "b", "&&", "c", "d", "|||", "e", "f"],
            [["a", "b"]],
            [["c", "d"], ["e", "f"]],
        )

        _check(
            ["monofy.py", "a", "b", "|||", "c", "d", "|||", "e", "f"],
            [],
            [["a", "b"], ["c", "d"], ["e", "f"]],
        )

        _check(
            ["monofy.py", "a", "b", "&&", "c", "d", "&&", "e", "f"],
            [["a", "b"], ["c", "d"]],
            [["e", "f"]],
        )

        _check(
            ["monofy.py", "a", "b", "&&", "c", "d", "&&", "e", "f", "|||", "g", "h", "|||", "i", "j"],
            [["a", "b"], ["c", "d"]],
            [["e", "f"], ["g", "h"], ["i", "j"]],
        )


if __name__ == '__main__':
    unittest.main()

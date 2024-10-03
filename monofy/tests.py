import os
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
            ["monofy.py", "a", "|||", "b", "|||", "c"],
            [],
            [["a"], ["b"], ["c"]],
        )

        _check(
            ["monofy.py", "a", "b", "|||", "c", "d", "|||", "e", "f"],
            [],
            [["a", "b"], ["c", "d"], ["e", "f"]],
        )

        _check(
            ["monofy.py", "a", "&&", "b", "|||", "c"],
            [["a"]],
            [["b"], ["c"]],
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

        _check(
            ["monofy.py", "$USER", "&&", "$USER", "|||", "$USER"],
            [[os.environ["USER"]]],
            [[os.environ["USER"]], [os.environ["USER"]]],
        )

    def test_substitute_env_vars(self):
        # test-the-test: we need a non-empty USER to be able to test against
        self.assertTrue(os.environ.get("USER"))

        self.assertEqual("donttouchme", ParentProcess.substitute_env_vars("donttouchme"))
        self.assertEqual("", ParentProcess.substitute_env_vars(""))
        self.assertEqual("foo %s" % os.environ["USER"], ParentProcess.substitute_env_vars("foo $USER"))
        self.assertEqual("bar %s foo" % os.environ["USER"], ParentProcess.substitute_env_vars("bar ${USER} foo"))
        self.assertEqual("", ParentProcess.substitute_env_vars("$THISWILLNOTEXIST"))
        self.assertEqual(
            "%s %s" % (os.environ["USER"], os.environ["USER"]), ParentProcess.substitute_env_vars("$USER $USER"))


if __name__ == '__main__':
    unittest.main()

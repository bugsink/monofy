import os
import subprocess
import sys
import unittest
from unittest import mock

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

        with mock.patch.dict(os.environ, {"USER": "test-user"}, clear=False):
            _check(
                ["monofy.py", "$USER", "&&", "$USER", "|||", "$USER"],
                [[os.environ["USER"]]],
                [[os.environ["USER"]], [os.environ["USER"]]],
            )

    def test_substitute_env_vars(self):
        with mock.patch.dict(os.environ, {"USER": "test-user"}, clear=False):
            self.assertEqual("donttouchme", ParentProcess.substitute_env_vars("donttouchme"))
            self.assertEqual("", ParentProcess.substitute_env_vars(""))
            self.assertEqual("foo %s" % os.environ["USER"], ParentProcess.substitute_env_vars("foo $USER"))
            self.assertEqual("bar %s foo" % os.environ["USER"], ParentProcess.substitute_env_vars("bar ${USER} foo"))
            self.assertEqual("", ParentProcess.substitute_env_vars("$THISWILLNOTEXIST"))
            self.assertEqual(
                "%s %s" % (os.environ["USER"], os.environ["USER"]), ParentProcess.substitute_env_vars("$USER $USER"))

    def test_connected_fates(self):
        proc = subprocess.run(
            [
                sys.executable,  # i.e. "python"
                "-m",
                "monofy.scripts.monofy",
                sys.executable,
                "-c",
                "import time; time.sleep(0.1)",
                "|||",
                sys.executable,
                "-c",
                # print 'got-sigterm' and exit with code 0 when receiving SIGTERM
                "import signal, sys, time; signal.signal(signal.SIGTERM, lambda *_: (print('got-sigterm', flush=True), sys.exit(0))); time.sleep(10)",
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        self.assertIn("got-sigterm", proc.stdout)


if __name__ == '__main__':
    unittest.main()

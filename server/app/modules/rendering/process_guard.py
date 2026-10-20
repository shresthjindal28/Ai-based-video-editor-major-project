"""Supervise one media process, including when its worker is killed abruptly.

This small stdlib-only child inherits the bounded output pipes and its own
process group. Parent death is detected through reparenting on POSIX systems.
"""
import os
import signal
import subprocess
import sys
import time


def main() -> int:
    parent = int(sys.argv[1])
    if os.getppid() != parent:
        return 1
    if os.getpgrp() != os.getpid():
        os.setsid()
    stopping = False

    def stop(signum, frame):
        nonlocal stopping
        stopping = True

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    process = subprocess.Popen(sys.argv[2:], stdin=subprocess.DEVNULL)
    while process.poll() is None:
        if stopping or os.getppid() != parent:
            # Ignore our own group signal while terminating all descendants.
            signal.signal(signal.SIGTERM, signal.SIG_IGN)
            os.killpg(os.getpgrp(), signal.SIGTERM)
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                os.killpg(os.getpgrp(), signal.SIGKILL)
            return 1
        time.sleep(0.1)
    return process.returncode if process.returncode >= 0 else 128-process.returncode


if __name__ == "__main__":
    sys.exit(main())

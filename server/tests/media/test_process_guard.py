import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

pytestmark=pytest.mark.media


def test_media_process_is_terminated_when_its_worker_exits(tmp_path: Path):
    pid_file=tmp_path/"media.pid"
    worker=tmp_path/"worker.py"
    media_code=f"import os,time; from pathlib import Path; Path({str(pid_file)!r}).write_text(str(os.getpid())); time.sleep(30)"
    worker.write_text("\n".join([
        "import subprocess,sys,os,time",
        "from pathlib import Path",
        f"pid_file=Path({str(pid_file)!r})",
        f"subprocess.Popen([sys.executable,'-m','app.modules.rendering.process_guard',str(os.getpid()),sys.executable,'-c',{media_code!r}],start_new_session=True)",
        "deadline=time.monotonic()+5",
        "while not pid_file.exists() and time.monotonic()<deadline: time.sleep(0.05)",
        "assert pid_file.exists()",
    ]))
    subprocess.run([sys.executable,str(worker)],check=True,timeout=10)
    pid=int(pid_file.read_text())
    deadline=time.monotonic()+8
    while time.monotonic()<deadline:
        try:
            os.kill(pid,0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    os.kill(pid,signal.SIGTERM)
    pytest.fail("Media child outlived its worker")

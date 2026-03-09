"""
Vast.ai Serverless PyWorker configuration.
Routes /transcribe requests to the local model server.

NOTE: Vast.ai Serverless ignores Docker CMD — it clones PYWORKER_REPO
and runs worker.py directly. So we must start model_server.py ourselves.
"""

import os
import subprocess

from vastai import (
    Worker,
    WorkerConfig,
    HandlerConfig,
    BenchmarkConfig,
    LogActionConfig,
)

# Start model server in background before PyWorker
os.makedirs("/var/log/model", exist_ok=True)
log_file = open("/var/log/model/server.log", "w")
subprocess.Popen(
    ["python3", "-u", "/app/model_server.py"],
    stdout=log_file,
    stderr=subprocess.STDOUT,
    cwd="/app",
)

worker_config = WorkerConfig(
    model_server_url="http://127.0.0.1",
    model_server_port=18001,
    model_log_file="/var/log/model/server.log",
    handlers=[
        HandlerConfig(
            route="/transcribe",
            allow_parallel_requests=False,
            max_queue_time=600,
            workload_calculator=lambda payload: 100.0,
            benchmark_config=BenchmarkConfig(
                generator=lambda: {
                    "audio_url": "https://www.kozco.com/tech/piano2-CoolEdit.mp3",
                    "language": "en",
                },
                runs=1,
                concurrency=1,
            ),
        ),
    ],
    log_action_config=LogActionConfig(
        on_load=["Running on http://"],
        on_error=["Traceback (most recent call last)", "RuntimeError"],
    ),
)

Worker(worker_config).run()

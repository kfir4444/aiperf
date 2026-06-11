#!/bin/bash
#SBATCH -A network_research_advdev
#SBATCH -p batch
#SBATCH -N 1
#SBATCH -t 00:30:00
#SBATCH --container-image=/lustre/fsw/network_research_advdev/kfkaplan/containers/image.sqsh
#SBATCH --container-mounts=/lustre/fsw/network_research_advdev/kfkaplan/Code/aiperf:/workspace
#SBATCH -J aiperf_profile
#SBATCH -o slurm-%j.out

# Move into your mounted workspace
cd /workspace

make first-time-setup

echo "=== Starting AIPerf Mock Server ==="
# 1. Start the server in the background and capture its Process ID (PID)
/root/.local/bin/uv run aiperf-mock-server \
    --port 8000 \
    --ttft 1000 \
    --itl 50 \
    --record-requests /tmp/aiperf-sine-requests.jsonl &
SERVER_PID=$!

# 2. Give the server 30 seconds to fully boot and bind to port 8000
sleep 30

echo "=== Starting Profiler ==="
# 3. Run the profiler in the foreground (this blocks until completion)
/root/.local/bin/uv run aiperf profile \
  --endpoint-type chat \
  --url http://localhost:8000 \
  --model Qwen/Qwen3-0.6B \
  --request-rate 8 \
  --request-rate-sine-frequency 0.1 \
  --request-rate-sine-amplitude 4 \
  --request-rate-sine-delay 0 \
  --benchmark-duration 60 \
  --isl-mean 128 \
  --osl-mean 128 \
  --random-range-ratio 0.1 \
  --ui simple

echo "=== Profiling Complete. Shutting down Mock Server ==="
# 4. Clean up the background server process
kill $SERVER_PID

echo "=== Running Data Verification Snippet ==="
# 5. Run your Python post-processing script
python - <<'PY'
import json, math
from collections import defaultdict
path = "/tmp/aiperf-sine-requests.jsonl"
starts = []
try:
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            starts.append(row.get("received_at") or row.get("timestamp") or row.get("start_time"))
    print("requests:", len(starts))
    print("sample raw timestamps:", starts[:5])
except FileNotFoundError:
    print(f"Error: {path} was not found. Check if the server recorded data correctly.")
PY

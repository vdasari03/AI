import json
import subprocess
import sys


def test_main_runs_and_outputs_json():
    # Run the main script and ensure valid JSON with recommendations
    proc = subprocess.run([sys.executable, "main.py"], capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    data = json.loads(proc.stdout)
    assert "recommendations" in data
    # new fields
    assert "executions" in data
    # recommendations should include symbol and action
    for r in data["recommendations"]:
        assert "symbol" in r
        assert "action" in r

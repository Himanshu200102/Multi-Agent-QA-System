import json, os, subprocess, sys, pathlib

def test_demo_runs():
    pkg = 'qa_agents.run_test'
    cmd = [sys.executable, '-m', pkg, '--goal', 'Toggle Wi‑Fi off and on', '--env', 'mock', '--logs_dir', '/mnt/data/qa_agents/logs']
    assert subprocess.call(cmd) == 0
    assert os.path.exists('/mnt/data/qa_agents/logs/qa_run.json')
    with open('/mnt/data/qa_agents/logs/qa_run.json') as f:
        data = json.load(f)
    assert isinstance(data, list) and len(data) > 0

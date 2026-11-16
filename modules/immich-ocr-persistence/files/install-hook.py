#!/usr/bin/env python3
"""Install the OCR startup hook and Dockge launcher, preserving the stack YAML."""
import json
from pathlib import Path
import shlex
import subprocess
import sys

CONFIG = Path.home() / '.config/immich-update/config.json'
ASSETS = Path.home() / '.local/share/immich-ocr'
def main():
    config = json.loads(CONFIG.read_text())
    ssh = ['ssh', '-F', str(Path.home() / '.ssh/config'), '-o', 'BatchMode=yes',
           '-o', 'ConnectTimeout=10', config['nas_ssh']]
    if '--check' in sys.argv:
        return subprocess.run(ssh + ['sudo -n docker exec immich-server node /opt/immich-ocr/apply.cjs']).returncode
    payload = {'stack': config['nas_stack'], 'files': {
        n: (ASSETS / n).read_text() for n in ['apply.cjs', 'update-nas.cjs']},
        'config': {'server_url': config['server_url'], 'worker_ping': config['worker_ping']}}
    # The remote program receives JSON as stdin, never shell-interpolated file content.
    script = (ASSETS / 'install-remote.py').read_text()
    subprocess.run(ssh + ['python3 -c ' + shlex.quote(script)],
                   input=json.dumps(payload), text=True, check=True)
    dockge_payload = {'stack': config['dockge_host_stack'],
                      'patch': (ASSETS / 'patch-dockge.cjs').read_text()}
    subprocess.run(ssh + ['python3 -c ' + shlex.quote((ASSETS / 'install-dockge.py').read_text())],
                   input=json.dumps(dockge_payload), text=True, check=True)
    return 0
if __name__ == '__main__':
    sys.exit(main())

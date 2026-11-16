"""Test notification deduplication without sending real desktop notifications."""
import ast
import json
from pathlib import Path
import subprocess
import tempfile
from unittest.mock import patch

tree=ast.parse((Path(__file__).parent/'files/immich-update.py').read_text())
function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='notify_ocr_status')
ns={'Path':Path,'json':json,'subprocess':subprocess}
exec(compile(ast.Module(body=[function],type_ignores=[]),'<notification>','exec'),ns)
with tempfile.TemporaryDirectory() as d:
    root=Path(d); status=root/'.immich-maintenance/ocr-status.json'
    status.parent.mkdir()
    states=[{'Mounts':[{'Destination':'/usr/src/app/upload','Source':d}]}]
    bad={'enabled':False,'reason':'incompatible','revision':'v1'}
    with patch.object(Path,'home',return_value=root), patch.object(subprocess,'run') as notify:
        status.write_text(json.dumps(bad))
        ns['notify_ocr_status'](states,'v3.4.2')
        ns['notify_ocr_status'](states,'v3.4.2')
        assert notify.call_count==1
        status.write_text('{"enabled":true}')
        ns['notify_ocr_status'](states,'v3.4.2')
        status.write_text(json.dumps(bad))
        ns['notify_ocr_status'](states,'v3.4.2')
        assert notify.call_count==2
        ns['notify_ocr_status'](states,'v3.4.3')
        assert notify.call_count==3
print('PASS desktop notification: warning, deduplication, recovery, version change')

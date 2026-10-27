import os
from pathlib import Path
import json
BASE=Path(os.environ['ROMS_NAS_DIR'])
rows=[]
for line in (BASE/'extraction-journal.jsonl').read_text().splitlines():
    try: rows.append(json.loads(line))
    except json.JSONDecodeError: pass
done={r['system'] for r in rows if r['event']=='system_done'}
active={r['system'] for r in rows if r['event']=='start'}-done
size=sum(f.stat().st_size for d in BASE.iterdir() if d.is_dir() for f in d.rglob('*') if f.is_file())
print(json.dumps(dict(completed=len(done),active=sorted(active),extracted_gb=round(size/1e9,2),errors=[r for r in rows if r['event']=='error'],finished=[r for r in rows if r['event']=='extraction_finished'],report_ready=(BASE/'INVENTAIRE-ROMs.json').exists()),ensure_ascii=False))

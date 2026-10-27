"""Run on the NAS after installing and verifying the local playlist references."""
import os
import json
from pathlib import Path

base=Path(os.environ['ROMS_NAS_LOCAL_DIR'])
data=json.loads((base/'integration-retroarch.json').read_text())
assert data['applied'] and data['rom_bytes_copied']==0
missing=[p['system'] for p in data['playlists'] if p['core']=='DETECT']
cores={p['system']:p['core'] if p['core']!='DETECT' else 'Non configuré' for p in data['playlists']}
report_path=base/'INVENTAIRE-ROMs.json'
report=json.loads(report_path.read_text())
for row in report['systems']:
    row['core']=cores[row['system']]
report['retroarch_integrated']=True
report['rom_bytes_copied_to_pc']=0
report_path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
section='\n'.join([
 '## Raccordement à ce PC effectué', '',
 f"Les {len(data['playlists'])} listes sont intégrées au RetroArch de `~/.config/retroarch/playlists/`. Leurs entrées pointent directement vers les jeux du NAS. **Aucune ROM copiée sur le PC.**",
 '', f"Raccourci de navigation : `{data['link']}`. Sauvegarde des anciennes listes : `{data['backup']}`.",
 '', 'Les noms des listes, leurs cœurs installés et les préréglages visuels existants sont conservés. Si RetroArch était ouvert pendant le raccordement, le relancer pour actualiser les listes.',
 '', 'Cœurs restant à configurer : '+', '.join(missing)+'. Les fichiers correspondants sont classés et référencés, mais leur lancement nécessite un cœur compatible.' if missing else '',
 '',
])
path=base/'INVENTAIRE-ROMs.md'
text=path.read_text()
heading,body=text.split('\n',1)
text=heading+'\n\n'+section+'\n'+body
lines=[]
for line in text.splitlines():
    if 'Copier uniquement ces petits fichiers' in line:
        line='Les modèles de listes `.lpl` restent disponibles dans `Playlists-RetroArch/` sur le NAS. Les listes actives de ce PC sont déjà installées localement et utilisent les chemins NAS. Les sauvegardes de parties et les réglages RetroArch restent locaux.'
    cells=line.split('|')
    if len(cells)==7 and cells[1].strip() in cores:
        cells[-2]=' '+cores[cells[1].strip()]+' '
        line='|'.join(cells)
    lines.append(line)
path.write_text('\n'.join(lines)+'\n')
print(json.dumps(dict(recorded=True,playlists=len(data['playlists']),missing_cores=missing),ensure_ascii=False))

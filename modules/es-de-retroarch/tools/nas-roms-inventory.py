#!/usr/bin/env python3
"""Finalize an entirely extracted set on the NAS; emit playlists and measured report."""
import os
import collections
import datetime
import fcntl
import json
from pathlib import Path
import re

BASE = Path(os.environ['ROMS_NAS_LOCAL_DIR'])
CLIENT = Path(os.environ['ROMS_NAS_DIR'])
# Generations are an organizational convention, with handhelds included.
SYSTEMS = {
    'Atari - 2600': ('2e', 'Atari - 2600', 'a26', 'Stella'),
    'Nintendo - NES': ('3e', 'Nintendo - Nintendo Entertainment System', 'nes fds', 'Mesen'),
    'Sega - Master System': ('3e', 'Sega - Master System - Mark III', 'sms', 'Genesis Plus GX'),
    'NEC - TurboGrafx-16': ('4e', 'NEC - PC Engine - TurboGrafx 16', 'pce', 'Beetle PCE FAST'),
    'NEC - TurboGrafx CD': ('4e', 'NEC - PC Engine CD - TurboGrafx-CD', 'chd m3u', 'Beetle PCE FAST'),
    'Nintendo - SNES': ('4e', 'Nintendo - Super Nintendo Entertainment System', 'sfc smc', 'Snes9x'),
    'Sega - Genesis': ('4e', 'Sega - Mega Drive - Genesis', 'md bin gen', 'Genesis Plus GX'),
    'Sega - Sega CD': ('4e', 'Sega - Mega-CD - Sega CD', 'chd m3u', 'Genesis Plus GX'),
    'Nintendo - Game Boy': ('4e', 'Nintendo - Game Boy', 'gb', 'Gambatte'),
    'Sega - Game Gear': ('4e', 'Sega - Game Gear', 'gg', 'Genesis Plus GX'),
    'Nintendo - Game Boy Color': ('5e', 'Nintendo - Game Boy Color', 'gbc gb', 'Gambatte'),
    'Nintendo - N64': ('5e', 'Nintendo - Nintendo 64', 'z64 n64 v64', 'Mupen64Plus-Next'),
    'Sony - PS1': ('5e', 'Sony - PlayStation', 'chd m3u', 'SwanStation'),
    'Sega - Saturn': ('5e', 'Sega - Saturn', 'chd m3u', 'Beetle Saturn'),
    'Nintendo - Game Boy Advance': ('6e', 'Nintendo - Game Boy Advance', 'gba', 'mGBA'),
    'Nintendo - GameCube': ('6e', 'Nintendo - GameCube', 'rvz iso m3u', 'Dolphin'),
    'Sega - Dreamcast': ('6e', 'Sega - Dreamcast', 'chd m3u', 'Flycast'),
    'Nintendo - DS': ('7e', 'Nintendo - Nintendo DS', 'nds', 'melonDS'),
    'Sony - PSP': ('7e', 'Sony - PlayStation Portable', 'iso cso', 'PPSSPP'),
    'Arcade - Mame 2003 Plus': ('Arcade', 'MAME 2003-Plus', 'zip', 'MAME 2003-Plus'),
    'SNK - NEO GEO': ('Arcade', 'SNK - Neo Geo', 'zip', 'Cœur compatible avec la version du romset'),
}

def write(path, text):
    temporary = path.with_suffix(path.suffix + '.tmp')
    temporary.write_text(text, encoding='utf-8')
    temporary.replace(path)

def main():
    journal = [json.loads(line) for line in (BASE / 'extraction-journal.jsonl').read_text().splitlines()]
    final = [r for r in journal if r['event'] == 'extraction_finished']
    assert final and not final[-1]['errors'], 'Extraction has not finished successfully'
    assert not list(BASE.glob('*.zip')), 'Outer archives remain'
    assert not list(BASE.rglob('*.extracting')), 'Incomplete extractions remain'
    assert all((BASE / name).is_dir() for name in SYSTEMS), 'Missing system folder'

    # Create relative multi-disc indexes where the target cores support them.
    for system in ('Sega - Dreamcast', 'Sega - Saturn', 'Sega - Sega CD', 'NEC - TurboGrafx CD', 'Nintendo - GameCube'):
        root = BASE / system
        groups = collections.defaultdict(list)
        for p in sorted(root.glob('*.chd')) + sorted(root.glob('*.rvz')):
            match = re.search(r' \(Disc (\d+)\)', p.stem)
            if match:
                name = re.sub(r' \(Disc \d+\)', '', p.stem)
                groups[name].append((int(match[1]), p))
        for name, discs in groups.items():
            if len(discs) > 1:
                text = ''.join(p.name + '\n' for _, p in sorted(discs))
                target = root / (name + '.m3u')
                if target.exists():
                    assert target.read_text().splitlines() == text.splitlines(), str(target)
                else:
                    write(target, text)

    playlists = BASE / 'Playlists-RetroArch'
    playlists.mkdir(exist_ok=True)
    rows = []
    for system, (generation, database, extensions, core) in SYSTEMS.items():
        root = BASE / system
        files = sorted(p for p in root.rglob('*') if p.is_file())
        if generation != 'Arcade':
            assert not any(p.suffix == '.zip' for p in files), system
        referenced = set()
        for p in files:
            if p.suffix == '.m3u':
                lines = [s.strip() for s in p.read_text(encoding='utf-8-sig').splitlines() if s.strip() and not s.startswith('#')]
                assert lines, str(p)
                for line in lines:
                    dest = (p.parent / line).resolve()
                    assert dest.is_relative_to(root.resolve()) and dest.is_file(), (p, line)
                    referenced.add(dest)
        allowed = {'.' + ext for ext in extensions.split()}
        entries = [p for p in files if p.suffix in allowed and p.resolve() not in referenced and p.name != 'neogeo.zip']
        unknown = [str(p.relative_to(root)) for p in files if p.suffix not in allowed and p.suffix not in {'.xml', '.txt', '.sav'}]
        assert not unknown, (system, unknown)
        items = [dict(path=str(CLIENT / p.relative_to(BASE)), label=p.stem, core_path='DETECT', core_name='DETECT', crc32='DETECT', db_name=database+'.lpl') for p in entries]
        data = dict(version='1.5', default_core_path='DETECT', default_core_name='DETECT', base_content_directory=str(CLIENT), items=items)
        write(playlists / (database + '.lpl'), json.dumps(data, ensure_ascii=False, indent=2)+'\n')
        rows.append(dict(system=system, generation=generation, entries=len(items), files=len(files), bytes=sum(p.stat().st_size for p in files), core=core, extensions=sorted({p.suffix for p in files})))
    generations = []
    for name in ('2e','3e','4e','5e','6e','7e','Arcade'):
        members = [row for row in rows if row['generation'] == name]
        generations.append(dict(generation=name, systems=[r['system'] for r in members], entries=sum(r['entries'] for r in members), bytes=sum(r['bytes'] for r in members)))
    removed = [r for r in journal if r['event']=='archive_removed']
    outer = [r for r in removed if '/' not in r['archive']]
    report = dict(date=datetime.datetime.now().isoformat(), client_path=str(CLIENT), systems=rows, generations=generations, total_bytes=sum(r['bytes'] for r in rows), total_entries=sum(r['entries'] for r in rows), outer_archives_removed=len(outer), outer_archive_bytes_removed=sum(r['bytes'] for r in outer), all_archive_bytes_removed=sum(r['bytes'] for r in removed), playlists=len(rows))
    write(BASE / 'INVENTAIRE-ROMs.json', json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    lines = ['# Jeux du NAS — extraction terminée', '', f'Inventaire du {report["date"]}. Tailles logiques mesurées : 1 Go = 1 000 000 000 octets ; hors compression, snapshots et allocation ZFS.', '', f'**{len(rows)} systèmes, {report["total_entries"]} entrées de lancement, {report["total_bytes"]/1e9:.3f} Go.**', '', '| Génération | Entrées | Taille (Go) |', '|---|---:|---:|']
    for r in generations:
        lines.append(f'| {r["generation"]} | {r["entries"]} | {r["bytes"]/1e9:.3f} |')
    lines += [f'| **Total** | **{report["total_entries"]}** | **{report["total_bytes"]/1e9:.3f}** |', '', 'Convention de classement : GB/Game Gear en 4e, GBC en 5e, GBA en 6e, DS/PSP en 7e. Neo Geo et MAME regroupés séparément dans Arcade. Les entrées ne sont pas un décompte garanti de titres uniques ; certains romsets arcade contiennent des variantes.', '', '| Dossier système | Génération | Entrées | Taille (Go) | Cœur |', '|---|---|---:|---:|---|']
    for r in rows:
        lines.append(f'| {r["system"]} | {r["generation"]} | {r["entries"]} | {r["bytes"]/1e9:.3f} | {r["core"]} |')
    lines += ['', '## Ouvrir dans RetroArch', '', f'Les jeux se trouvent sous `{CLIENT}/`, avec un dossier par système.', '', f'Les {len(rows)} listes `.lpl` sont prêtes dans `{CLIENT}/Playlists-RetroArch/`. Copier uniquement ces petits fichiers vers le dossier de playlists local de RetroArch (`~/.config/retroarch/playlists/`) pour garder les listes modifiables : le montage NAS de ce PC est en lecture seule. Les ROMs restent sur le NAS. Choisir ensuite un cœur pour chaque liste dans Réglages → Listes de lecture → Gérer les listes de lecture. Les chemins intégrés correspondent à ce PC.', '', 'On peut aussi ouvrir directement un jeu via Charger du contenu. Pour PS1, Dreamcast, Saturn et GameCube, privilégier le `.m3u` lorsqu’il existe : ses disques sont regroupés dans une seule entrée.', '', 'Les archives des ROMs Arcade/Neo Geo sont conservées en ZIP : ce sont les jeux utilisables par leurs cœurs, pas des copies superflues. Le fichier `neogeo.zip` est conservé mais exclu du menu de jeux. Les BIOS et la compatibilité des cœurs restent à vérifier par la configuration RetroArch ; aucun test d’exécution des jeux n’a été effectué ici.', '', '## Vérification et nettoyage', '', f'{len(outer)} archives de collections supprimées après extraction et relecture CRC32 : {report["outer_archive_bytes_removed"]/1e9:.3f} Go de copies compressées retirées. Les ZIP internes des consoles ont également été extraits, vérifiés puis supprimés. Ce chiffre ne représente pas le gain net par rapport au lot initial, puisque les jeux extraits prennent leur place.', '', 'Les parties alphabétiques et mises à jour sont réunies dans leurs dossiers système. Aucun fichier existant de contenu différent n’est écrasé. Les liens de tous les M3U sont contrôlés. Journal détaillé : `extraction-journal.jsonl` ; données exactes : `INVENTAIRE-ROMs.json`.', '', 'Documentation : [listes RetroArch](https://docs.libretro.com/guides/roms-playlists-thumbnails/), [romsets arcade](https://docs.libretro.com/guides/arcade-getting-started/), [multidisques Dreamcast](https://docs.libretro.com/library/flycast/), [Saturn](https://docs.libretro.com/library/beetle_saturn/).', '']
    write(BASE / 'INVENTAIRE-ROMs.md', '\n'.join(lines))
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    with (BASE / '.extraction.lock').open('r') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        main()

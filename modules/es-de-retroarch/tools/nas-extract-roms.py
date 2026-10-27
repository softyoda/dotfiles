#!/usr/bin/env python3
"""Run on the NAS. CRC-verified, restartable extraction; never overwrite conflicts."""
import collections
import concurrent.futures
import datetime
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import threading
import zipfile
import zlib

BASE = Path(os.environ['ROMS_NAS_LOCAL_DIR'])
LOCK = threading.Lock()
KEEP_ZIPS = {'Arcade - Mame 2003 Plus', 'SNK - NEO GEO'}
os.umask(0o022)

def log(event, **data):
    row = dict(time=datetime.datetime.now().isoformat(), event=event, **data)
    with LOCK:
        print(json.dumps(row, ensure_ascii=False), flush=True)
        with (BASE / 'extraction-journal.jsonl').open('a') as f:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
            f.flush()
            os.fsync(f.fileno())

def crc(path):
    value = 0
    with path.open('rb') as f:
        while block := f.read(8 * 1024 * 1024):
            value = zlib.crc32(block, value)
    return value & 0xffffffff

def target(root, name):
    p = PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name:
        raise ValueError('Unsafe archive path: ' + name)
    dest = root.joinpath(*p.parts)
    if not dest.resolve().is_relative_to(root.resolve()):
        raise ValueError('Escaping symlink: ' + str(dest))
    if dest.is_symlink():
        raise ValueError('Destination symlink: ' + str(dest))
    return dest

def unpack(archive, root):
    original = archive.stat()
    rows = []
    with zipfile.ZipFile(archive) as z:
        entries = z.infolist()
        names = set()
        for info in entries:
            target(root, info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('Archive symlink: ' + info.filename)
            if info.filename in names:
                raise ValueError('Duplicate archive entry: ' + info.filename)
            names.add(info.filename)
        for info in entries:
            dest = target(root, info.filename)
            if info.is_dir():
                dest.mkdir(parents=True, exist_ok=True)
                continue
            dest.parent.mkdir(parents=True, exist_ok=True)
            if dest.exists():
                if dest.stat().st_size != info.file_size or crc(dest) != info.CRC:
                    raise ValueError('Existing file differs, preserved: ' + str(dest))
            else:
                partial = dest.with_name(dest.name + '.extracting')
                if partial.is_symlink():
                    raise ValueError('Partial file is symlink')
                with z.open(info) as src, partial.open('wb') as out:
                    while block := src.read(8 * 1024 * 1024):
                        out.write(block)
                    out.flush()
                    os.fsync(out.fileno())
                if partial.stat().st_size != info.file_size or crc(partial) != info.CRC:
                    raise ValueError('Written file CRC mismatch: ' + str(partial))
                os.rename(partial, dest)
                fd = os.open(dest.parent, os.O_DIRECTORY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)
            rows.append(dict(path=str(dest.relative_to(BASE)), size=info.file_size, crc32=f'{info.CRC:08x}'))
    current = archive.stat()
    if (current.st_size, current.st_mtime_ns) != (original.st_size, original.st_mtime_ns):
        raise ValueError('Archive changed during extraction: ' + str(archive))
    log('verified', archive=str(archive.relative_to(BASE)), bytes=original.st_size, files=rows)
    return original

def delete_verified(archive, original):
    current = archive.stat()
    if (current.st_size, current.st_mtime_ns) != (original.st_size, original.st_mtime_ns):
        raise ValueError('Archive changed before deletion')
    archive.unlink()
    log('archive_removed', archive=str(archive.relative_to(BASE)), bytes=original.st_size)

def system_name(archive):
    return re.sub(r' \((?:[A-Z]-[A-Z]|Update \d+)\)$', '', archive.stem)

def process(system, archives):
    root = BASE / system
    root.mkdir(exist_ok=True)
    # Unpack every outer archive before nested ZIPs so restarts can compare entries.
    for archive in sorted(archives, key=lambda p: ('Update' in p.name, p.name)):
        log('start', archive=archive.name, system=system)
        original = unpack(archive, root)
        delete_verified(archive, original)
        log('outer_done', archive=archive.name, system=system)
    if system not in KEEP_ZIPS:
        for archive in sorted(root.rglob('*.zip')):
            original = unpack(archive, archive.parent)
            delete_verified(archive, original)
    else:
        for archive in sorted(root.glob('*.zip')):
            with zipfile.ZipFile(archive) as z:
                bad = z.testzip()
                if bad:
                    raise ValueError(f'Arcade ZIP corrupted: {archive}: {bad}')
        log('arcade_zip_integrity_verified', system=system)
    log('system_done', system=system)

def main():
    with (BASE / '.extraction.lock').open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        groups = collections.defaultdict(list)
        for archive in BASE.glob('*.zip'):
            groups[system_name(archive)].append(archive)
        for root in BASE.iterdir():
            if root.is_dir() and ' - ' in root.name:
                groups.setdefault(root.name, [])
        errors = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(process, system, archives): system for system, archives in sorted(groups.items(), key=lambda item: sum(p.stat().st_size for p in item[1]))}
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    errors.append(dict(system=futures[future], error=str(e)))
                    log('error', **errors[-1])
        log('extraction_finished', errors=errors)
        if errors:
            raise SystemExit(1)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Update package versions and fetchurl hashes without evaluating Nix."""

import base64
import hashlib
import json
import re
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VERSION = r'[0-9]+(?:\.[0-9]+)+'
VERSION_PATTERN = r'(?m)^(\s*version\s*=\s*")(' + VERSION + r')(";)'
SOURCE_PATTERN = r'(\bsrc\s*=\s*fetchurl\s*\{[^}]*?\bhash\s*=\s*")([^"\n]+)(";)'


def curl(url, output):
    subprocess.run(['curl', '-fsSL', '--globoff', '--retry', '2', '--connect-timeout', '15',
                    '--max-time', '600', '--output', str(output), url], check=True)


def parse_version(package, data):
    if package == 'baidunetdisk':
        results = json.loads(data)['results']
        if len(results) != 1:
            raise ValueError('Expected exactly one AUR result')
        version = re.sub(r'-[^-]+$', '', results[0]['Version'])
    elif package == 'lceda-pro':
        versions = set(re.findall(r'lceda-pro-linux-x64-(' + VERSION + r')\.zip', data))
        if len(versions) != 1:
            raise ValueError(f'Expected exactly one LCEDA version, found {versions}')
        version = versions.pop()
    else:
        raise ValueError(f'Unknown package: {package}')
    if not re.fullmatch(VERSION, version):
        raise ValueError(f'Invalid version: {version}')
    return version


def latest_version(package):
    urls = {
        'baidunetdisk': 'https://aur.archlinux.org/rpc/?v=5&type=info&arg[]=baidunetdisk-electron',
        'lceda-pro': 'https://lceda.cn/page/download',
    }
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'metadata'
        curl(urls[package], path)
        return parse_version(package, path.read_text(encoding='utf-8'))


def source_url(package, version):
    if package == 'baidunetdisk':
        return f'http://wppkg.baidupcs.com/issue/netdisk/Linuxguanjia/{version}/baidunetdisk_{version}_amd64.deb'
    if package == 'lceda-pro':
        return f'https://image.lceda.cn/files/lceda-pro-linux-x64-{version}.zip'
    raise ValueError(f'Unknown package: {package}')


def source_hash(url):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / 'source'
        curl(url, path)
        digest = hashlib.sha256()
        with path.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                digest.update(chunk)
        return 'sha256-' + base64.b64encode(digest.digest()).decode('ascii')


def replace_one(text, pattern, value):
    result, count = re.subn(pattern, lambda match: match.group(1) + value + match.group(3), text, flags=re.DOTALL)
    if count != 1:
        raise ValueError(f'Expected one match, found {count}: {pattern}')
    return result


def update_package(package, path):
    original = path.read_text(encoding='utf-8')
    versions = re.findall(VERSION_PATTERN, original)
    if len(versions) != 1:
        raise ValueError(f'Expected one version in {path}, found {len(versions)}')
    current = versions[0][1]
    latest = latest_version(package)
    print(f'{package}: {current} -> {latest}', flush=True)
    if latest == current:
        return
    if tuple(map(int, latest.split('.'))) < tuple(map(int, current.split('.'))):
        raise ValueError(f'Refusing to downgrade {package} from {current} to {latest}')
    updated = replace_one(original, VERSION_PATTERN, latest)
    updated = replace_one(updated, SOURCE_PATTERN, source_hash(source_url(package, latest)))
    path.write_text(updated, encoding='utf-8')


def main():
    for package in ('baidunetdisk', 'lceda-pro'):
        update_package(package, ROOT / 'pkgs' / package / 'default.nix')


if __name__ == '__main__':
    main()

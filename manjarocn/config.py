import os
from pathlib import Path

__all__ = ['root', 'env', 'pkglist']

root = Path(__file__).parent.parent


def parse_env():
    _env = {
        'CI': False,
        'SHELL': '/bin/bash',
        'BRANCH': 'stable',
        'ARCH': 'x86_64',
        'IMAGE': 'manjarocn/base:%s-latest',
        'MAKEFLAGS': '-j%d' % (os.cpu_count() + 1),
    }
    _env['IMAGE'] = _env['IMAGE'] % _env['BRANCH']
    _env = {k: os.environ.get(k, v) for k, v in _env.items()}

    paths = {
        'ARCHCN': ['../archlinuxcn_repo/archlinuxcn', '/build/workspace'],
        'GPGDIR': ['~/.gnupg', '/gpg'],
        'PKGCACHE': ['../pkgcache', '/pkgcache'],
        'PKGDEST': ['../build/packages', '/build/packages'],
        'SRCDEST': ['../build/sources', '/build/sources'],
        'SRCPKGDEST': ['../build/srcpackages', '/build/srcpackages'],
    }
    _env['PATHS'] = {}
    for name, (target, link) in paths.items():
        target = os.environ.get(name, target)
        target = root / target if target.startswith('.') else Path(target)
        target = target.expanduser().resolve()
        if not target.is_dir():
            if name in ['ARCHCN', 'GPGDIR']:
                raise FileNotFoundError(target)
            target.mkdir(0o755, True, True)
        _env['PATHS'][name] = [target, link]

    return _env


def parse_pkglist():
    names = [
        'list',
        'blacklist',
        'largelist'
    ]

    _pkglist = {}
    for n in names:
        with (root / 'pkglist' / (n + '.txt')).open(encoding='utf8') as f:
            _pkglist[n] = [i.strip() for i in f]
    _pkglist['list'] = [env['PATHS']['ARCHCN'][0].glob(i.strip()) for i in _pkglist['list']]
    _pkglist['list'] = [j.name for i in _pkglist['list'] for j in i]

    return _pkglist


env = parse_env()
pkglist = parse_pkglist()

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
        'IMAGE': 'manjarocn/base:{branch}-latest',
        'MAKEFLAGS': '-j%d' % (os.cpu_count() + 1),
        'PROXY': None,
    }
    _env = {k: os.environ.get(k, v) for k, v in _env.items()}
    _env['IMAGE'] = _env['IMAGE'].format(branch=_env['BRANCH'], arch=_env['ARCH'])

    paths = {
        'ARCHCN': ['../archlinuxcn_repo/archlinuxcn', '/build/workspace'],
        'GPGDIR': ['~/.gnupg', '/gpg'],
        'PKGDEST': ['../build/packages', '/build/packages'],
        'SRCDEST': ['../build/sources', '/build/sources'],
        'SRCPKGDEST': ['../build/srcpackages', '/build/srcpackages'],
        'PACMANDB': ['../pacmandb/{branch}/{arch}', '/var/lib/pacman/sync'],
        'PKGCACHE': ['../pkgcache/{branch}/{arch}', '/var/cache/pacman/pkg'],
    }
    _env['PATHS'] = {}
    for name, (target, link) in paths.items():
        target = os.environ.get(name, target)
        target = target.format(branch=_env['BRANCH'], arch=_env['ARCH'])
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

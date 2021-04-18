import sys
import re
import subprocess
from datetime import datetime

from .config import env

__all__ = ['prin', 'parse_pkgbuild', 'get_pkg_version', 'get_pkg_architecture', 'get_pkg_depends']


def prin(*args, error=False, color=92, **kwargs):
    print(
        '\033[%dm%s' % (color, datetime.utcnow()),
        '\U0001f449 ManjaroCN --->',
        *args,
        file=sys.stderr if error else sys.stdout,
        **kwargs,
    )
    print('\033[0m', end='')


def parse_pkgbuild(pkgbuild, var, required=False):
    cmd = 'set -euo pipefail; source %s >/dev/null; ' % pkgbuild
    cmd += 'set -u; ' if required else 'set +u; '
    cmd += 'echo -n "%s"' % var

    try:
        s = subprocess.run([env['SHELL'], '-c', cmd],
                           check=True, encoding='utf8', stdout=subprocess.PIPE)
    except subprocess.CalledProcessError:
        raise ValueError('parse PKGBUILD failed')

    val = s.stdout.strip()
    if required and not val:
        raise ValueError('%s is empty' % var)
    return val


def get_pkg_version(pkgbuild):
    pkgver = '%s-%s' % (
        parse_pkgbuild(pkgbuild, '$pkgver', True),
        parse_pkgbuild(pkgbuild, '$pkgrel', True),
    )
    epoch = parse_pkgbuild(pkgbuild, '$epoch')
    if epoch:
        pkgver = '%s:%s' % (epoch, pkgver)
    return pkgver


def get_pkg_architecture(pkgbuild):
    arch = parse_pkgbuild(pkgbuild, '${arch[@]}', True)
    arch = arch.split()
    if env['ARCH'] in arch:
        return env['ARCH']
    if 'any' in arch:
        return 'any'
    raise ValueError('unsupported architecture')


def get_pkg_depends(pkgbuild):
    depends = '%s %s' % (
        parse_pkgbuild(pkgbuild, '${makedepends[@]}'),
        parse_pkgbuild(pkgbuild, '${depends[@]}'),
    )
    depends = [re.split('[>=<]', i, 1)[0] for i in depends.strip().split()]
    depends = [i for i in depends if (env['PATHS']['ARCHCN'][0] / i).is_dir()]
    return depends

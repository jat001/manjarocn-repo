#!/usr/bin/python3

import os
import subprocess
from pathlib import Path


def parse_env():
    image = os.environ.get('IMAGE', 'manjarocn/base:latest')
    makeflags = os.environ.get('MAKEFLAGS', '-j%d' % (os.cpu_count() + 1))
    paths = {
        'ARCHCN': ['../archlinuxcn_repo/archlinuxcn', '/build'],
        'GPGDIR': ['~/.gnupg', '/gpg'],
        'PKGDEST': ['/build/packages', '/build/packages'],
        'SRCDEST': ['/build/sources', '/build/sources'],
        'SRCPKGDEST': ['/build/srcpackages', '/build/srcpackages'],
        'LOGDEST': ['/build/makepkglogs', '/build/makepkglogs'],
        'PKGCACHE': ['/build/pkgcache', '/pkgcache'],
    }

    for k, v in paths.items():
        v[0] = os.environ.get(k, v[0])
        v[0] = Path(v[0]).expanduser().resolve()
        if not v[0].is_dir():
            if k in ['ARCHCN', 'GPGDIR']:
                raise FileNotFoundError(v[0])
            v[0].mkdir(0o755, True, True)

    return {
        'image': image,
        'makeflags': makeflags,
        'paths': paths,
    }


def build(pkg, env, errors):
    root = env['paths']['ARCHCN'][0] / pkg

    if not (root / 'PKGBUILD').is_file():
        errors.append([pkg, 'PKGBUILD not found'])
        return False

    cmd = ['docker', 'run', '--rm', '-e', 'MAKEFLAGS=' + env['makeflags']]

    for k, v in env['paths'].items():
        cmd.extend(['-v', '%s:%s:%s' % (
            v[0] if k != 'ARCHCN' else root,
            v[1],
            'rw' if k != 'GPGDIR' else 'ro',
        )])

    cmd.append(env['image'])
    print('Building %s:' % pkg, cmd)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        errors.append([pkg, e])
        return False

    return True


def main():
    env = parse_env()
    print('Build env vars:', env)

    errors = []
    with (Path(__file__).parent / 'list.txt').open() as f:
        for pkg in f:
            build(pkg.strip(), env, errors)

    if errors:
        print('Build error:')
        for e in errors:
            print(e[0], e[1])


if __name__ == '__main__':
    main()

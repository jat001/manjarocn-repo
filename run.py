#!/usr/bin/python3

import os
import sys
import re
import subprocess
from pathlib import Path
from datetime import datetime


def prin(*args, pkg=None, error=False, **kwargs):
    print(datetime.now(), ':point_right: ManjaroCN --->', *args,
          '%s --->' % pkg if pkg is not None else '',
          file=sys.stderr if error else sys.stdout, **kwargs)


def parse_env():
    shell = os.environ.get('SHELL', '/bin/bash')
    branch = os.environ.get('BRANCH', 'stable')
    image = os.environ.get('IMAGE', 'manjarocn/base:%s-latest' % branch)
    makeflags = os.environ.get('MAKEFLAGS', '-j%d' % (os.cpu_count() + 1))
    paths = {
        'ARCHCN': ['../archlinuxcn_repo/archlinuxcn', '/build/workspace'],
        'GPGDIR': ['~/.gnupg', '/gpg'],
        'PKGCACHE': ['../pkgcache', '/pkgcache'],
        'PKGDEST': ['../build/packages', '/build/packages'],
        'SRCDEST': ['../build/sources', '/build/sources'],
        'SRCPKGDEST': ['../build/srcpackages', '/build/srcpackages'],
    }

    for k, v in paths.items():
        v[0] = os.environ.get(k, v[0])
        v[0] = Path(v[0]).expanduser().resolve()
        if not v[0].is_dir():
            if k in ['ARCHCN', 'GPGDIR']:
                raise FileNotFoundError(v[0])
            v[0].mkdir(0o755, True, True)

    return {
        'shell': shell,
        'branch': branch,
        'image': image,
        'makeflags': makeflags,
        'paths': paths,
    }


def build(pkg, env, blacklist, errors, depends_tree=None):
    pkgbuild = env['paths']['ARCHCN'][0] / pkg / 'PKGBUILD'
    if not pkgbuild.is_file():
        errors.append([pkg, 'PKGBUILD not found'])
        prin('build failed: PKGBUILD not found', pkg=pkg, error=True)
        return False

    if pkg in blacklist:
        errors.append([pkg, 'package in blacklist'])
        prin('build failed: package in blacklist', pkg=pkg, error=True)
        return False

    if depends_tree is None:
        depends_tree = []
    depends_tree.append(pkg)
    prin('depends tree:', depends_tree, pkg=pkg)
    if len(depends_tree) > 10:
        errors.append([pkg, 'depends too deep'])
        prin('build failed: depends too deep', pkg=pkg, error=True)
        return False

    depends = subprocess.run([
        env['shell'], '-c',
        'source %s; echo -n "${depends[@]}"; echo -n " ${makedepends[@]}"' % pkgbuild.as_posix(),
    ], stdout=subprocess.PIPE)
    depends = [re.split('>|=|<', i)[0] for i in depends.stdout.decode('utf8').split()]
    depends = [i for i in depends if (env['paths']['ARCHCN'][0] / i).is_dir()]
    if depends:
        prin('found depends:', depends, pkg=pkg)
        for i in depends:
            if not build(i, env, blacklist, errors, depends_tree):
                prin('build depend %s failed:' % i, pkg=pkg, error=True)
                return False

    cmd = ['docker', 'run', '--rm', '-e', 'MAKEFLAGS=' + env['makeflags']]
    for k, v in env['paths'].items():
        cmd.extend(['-v', '%s:%s:%s' % (
            v[0] if k != 'ARCHCN' else env['paths']['ARCHCN'][0] / pkg,
            v[1],
            'rw' if k != 'GPGDIR' else 'ro',
        )])
    cmd.append(env['image'])
    prin('building:', cmd, pkg=pkg)

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        errors.append([pkg, e])
        prin('build failed:', e, pkg=pkg, error=True)
        return False

    return True


def main():
    env = parse_env()
    prin('Build env vars:', env)

    with (Path(__file__).parent / 'blacklist.txt').open(encoding='utf8') as f:
        blacklist = {i.strip() for i in f}

    errors = []
    with (Path(__file__).parent / 'list.txt').open(encoding='utf8') as f:
        for i in f:
            i = env['paths']['ARCHCN'][0].glob(i.strip())
            for j in i:
                build(j.name, env, blacklist, errors)

    if errors:
        prin('Build errors:', error=True)
        for e in errors:
            prin(e[0], e[1], error=True)


if __name__ == '__main__':
    main()

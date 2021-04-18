import platform
import subprocess

from .config import *
from .error import *
from .utils import *


class Builder:
    def __init__(self, pkg, depends_tree=None):
        self.pkg = pkg
        self.pkgbuild = env['PATHS']['ARCHCN'][0] / self.pkg / 'PKGBUILD'
        if not self.pkgbuild.is_file():
            raise self.log_error(PKGBUILDNotFound)

        if self.pkg in pkglist['blacklist']:
            raise self.log_error(PackageInBlackList)

        if env['CI'] and self.pkg in pkglist['largelist']:
            raise self.log_error(PackageInLargeList)

        self.arch = self.get_arch()
        self.pkgver = self.get_pkgver()
        self.depends_tree = [] if depends_tree is None else depends_tree.copy()

    def print_log(self, *args, **kwargs):
        prin('%s --->' % self.pkg, *args, **kwargs)

    def log_error(self, reason):
        self.print_log(reason.error, error=True, color=reason.color)
        return reason(self.pkg)

    def get_arch(self):
        try:
            return get_pkg_architecture(self.pkgbuild.as_posix())
        except ValueError:
            raise self.log_error(ParsePKGBUILDError)

    def get_pkgver(self):
        try:
            pkgver = get_pkg_version(self.pkgbuild.as_posix())
        except ValueError:
            raise self.log_error(ParsePKGBUILDError)

        filename = '%s-%s-%s.pkg.tar.zst' % (
            self.pkg,
            pkgver.replace(':', '\uf03a') if platform.system() == 'Windows' else pkgver,
            self.arch,
        )
        path = env['PATHS']['PKGDEST'][0] / env['BRANCH'] / env['ARCH'] / filename
        if path.is_file():
            raise self.log_error(PackageUpToDate)

        return pkgver

    def build_depends(self):
        self.depends_tree.append(self.pkg)
        if len(self.depends_tree) > 10:
            self.log_error(DependsTooDeep)

        try:
            depends = get_pkg_depends(self.pkgbuild.as_posix())
        except ValueError:
            raise self.log_error(ParsePKGBUILDError)

        if depends:
            self.print_log('found depends:', depends)
            for i in depends:
                Builder(i, self.depends_tree).build()

    def build(self):
        self.build_depends()

        self.print_log('package version:', self.pkgver)
        cmd = ['docker', 'run', '--rm', '-e', 'MAKEFLAGS=' + env['MAKEFLAGS']]
        for name, (target, link) in env['PATHS'].items():
            if name == 'ARCHCN':
                target /= self.pkg
            mode = 'ro' if name == 'GPGDIR' else 'rw'

            cmd.extend(['-v', '%s:%s:%s' % (
                target,
                link,
                mode,
            )])
        cmd.append(env['IMAGE'])
        self.print_log('build command:', cmd)

        try:
            subprocess.run(cmd, check=True, encoding='utf8')
        except subprocess.CalledProcessError:
            raise self.log_error(BuildFailed)

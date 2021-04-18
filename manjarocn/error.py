from .utils import prin

__all__ = ['Errors', 'BaseError', 'PKGBUILDNotFound', 'PackageInBlackList', 'PackageInLargeList',
           'DependsTooDeep', 'PackageUpToDate', 'ParsePKGBUILDError', 'BuildFailed']


class Errors:
    errors = []

    @classmethod
    def append(cls, error):
        cls.errors.append(error)

    @classmethod
    def print(cls):
        if cls.errors:
            print('\n\n\n', end='')
            prin('build errors:', error=True, color=91)
            for error in cls.errors:
                prin(error.pkg, '--->', error.error, error=True, color=error.color)


class BaseError(Exception):
    pkg = 'unknown_pkg'
    error = 'build failed: unknown error'
    color = 91

    def __init__(self, pkg):
        self.pkg = pkg
        Errors.append(self)


class PKGBUILDNotFound(BaseError):
    error = 'skip build: PKGBUILD Not Found'


class PackageInBlackList(BaseError):
    error = 'skip build: package in blacklist'
    color = 93


class PackageInLargeList(BaseError):
    error = 'skip build: package in largelist'
    color = 93


class DependsTooDeep(BaseError):
    error = 'skip build: depends are too deep'


class PackageUpToDate(BaseError):
    error = 'skip build: package is up to date'
    color = 96


class ParsePKGBUILDError(BaseError):
    error = 'skip build: parse PKGBUILD failed'


class BuildFailed(BaseError):
    error = 'build failed: command returned non-zero exit status'

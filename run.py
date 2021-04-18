#!/usr/bin/python3
import sys

from manjarocn.config import *
from manjarocn.utils import prin
from manjarocn.builder import Builder
from manjarocn.error import BaseError, Errors


def main():
    prin('build env vars:', env)

    packages = pkglist['list']
    if len(sys.argv) > 1:
        packages = sys.argv[1:]

    for i in packages:
        try:
            Builder(i).build()
        except BaseError:
            pass

    if Errors.errors:
        Errors.print()


if __name__ == '__main__':
    main()

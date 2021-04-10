# Manjaro CN Repository

Automatically built packages based on [archlinuxcn/repo](https://github.com/archlinuxcn/repo) and [manjarocn/docker](https://github.com/manjarocn/docker).

## Install

Add `manjarocn` to `/etc/pacman.conf`:

 > Please make sure `manjarocn` is before `archlinuxcn` if you also use `archlinuxcn` repository.

```
[manjarocn]
Server = https://repo.manjarocn.org/stable/x86_64
```

Import GPG keys:

```
sudo pacman-key --recv-keys 974B3711CFB9BF2D && sudo pacman-key --lsign-key 974B3711CFB9BF2D
```

## Package List

See [/gh-pages/stable/x86_64](https://github.com/manjarocn/repo/tree/gh-pages/stable/x86_64)

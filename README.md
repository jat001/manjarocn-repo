# manjarocn/repo

基于 [archlinuxcn/repo](https://github.com/archlinuxcn/repo) 和 [manjarocn/docker](https://github.com/manjarocn/docker) 的自动化构建

```
[manjarocn]
Server = https://repo.manjarocn.org/stable/x86_64

sudo pacman-key --recv-keys 974B3711CFB9BF2D && sudo pacman-key --lsign-key 974B3711CFB9BF2D
```

## 开发状态

刚跑通流程，还没写完自动化构建，只有几个半自动打的包，不建议用于生产环境

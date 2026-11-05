# nur-packages

我的个人 [NUR](https://github.com/nix-community/NUR) 软件包仓库，支持通过 Nix Flake 使用。

## 软件包

| 包名 | 说明 | 平台 |
| --- | --- | --- |
| `baidunetdisk` | 百度网盘 Linux 客户端（非自由软件） | `x86_64-linux` |
| `lceda-pro` | 嘉立创EDA专业版 Linux 客户端（非自由软件） | `x86_64-linux` |


百度网盘使用上游的 Debian 安装包，通过 FHS 环境运行。启动脚本会传入 `--no-sandbox`。

嘉立创EDA专业版使用官方 Linux 客户端，保留上游的发行许可文件。首次使用可能需要导入官方激活文件。

## 开发

```sh
nix develop                 # 进入开发环境并启用 Git hooks
nix fmt                     # 格式化 Nix 和 shell 文件
nix flake check             # 运行仓库检查
```

开发环境、格式化器和检查目前配置在 `x86_64-linux` 上。百度网盘和嘉立创EDA专业版分别使用 [`pkgs/baidunetdisk/update.sh`](./pkgs/baidunetdisk/update.sh) 和 [`pkgs/lceda-pro/update.sh`](./pkgs/lceda-pro/update.sh) 检查版本。GitHub Actions 每周一在同一任务中检查两个包，仅构建发生变化的包，并为更新创建一个 PR；可以在 Actions 页面手动触发。

## 许可证

仓库代码采用 [MIT 许可证](./LICENSE)。各软件包的许可由其自身的 `meta.license` 指定；百度网盘和嘉立创EDA专业版为非自由软件。

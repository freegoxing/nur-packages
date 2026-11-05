# nur-packages

我的个人 [NUR](https://github.com/nix-community/NUR) 软件包仓库，支持通过 Nix Flake 使用。

## 软件包

| 包名 | 说明 | 平台 |
| --- | --- | --- |
| `baidunetdisk` | 百度网盘 Linux 客户端（非自由软件） | `x86_64-linux` |
| `lceda-pro` | 嘉立创EDA专业版 Linux 客户端（非自由软件） | `x86_64-linux` |
| `example-package` | NUR 模板附带的示例包 | 取决于构建平台 |

百度网盘使用上游的 Debian 安装包，通过 FHS 环境运行。启动脚本会传入 `--no-sandbox`。

嘉立创EDA专业版使用官方 Linux 客户端，保留上游的发行许可文件。首次使用可能需要导入官方激活文件。

## 使用

启用 Nix 的 `nix-command` 和 `flakes` 实验功能后，可以直接构建或运行百度网盘：

```sh
NIXPKGS_ALLOW_UNFREE=1 nix build --impure github:freegoxing/nur-packages#baidunetdisk
NIXPKGS_ALLOW_UNFREE=1 nix run --impure github:freegoxing/nur-packages#baidunetdisk
NIXPKGS_ALLOW_UNFREE=1 nix run --impure github:freegoxing/nur-packages#lceda-pro
```

也可以在 Flake 中添加输入：

```nix
inputs.nur-packages.url = "github:freegoxing/nur-packages";
```

随后从 `inputs.nur-packages.packages.x86_64-linux.baidunetdisk` 引用软件包。该 Flake 自行导入 nixpkgs；求值百度网盘时可设置 `NIXPKGS_ALLOW_UNFREE=1` 并使用 `--impure`。

## 开发

```sh
nix develop                 # 进入开发环境并启用 Git hooks
nix fmt                     # 格式化 Nix 和 shell 文件
nix flake check             # 运行仓库检查
```

开发环境、格式化器和检查目前配置在 `x86_64-linux` 上。百度网盘和嘉立创EDA专业版分别使用 [`pkgs/baidunetdisk/update.sh`](./pkgs/baidunetdisk/update.sh) 和 [`pkgs/lceda-pro/update.sh`](./pkgs/lceda-pro/update.sh) 检查版本。GitHub Actions 每天在同一任务中检查两个包，仅构建发生变化的包，并为更新创建一个 PR；可以在 Actions 页面手动触发。

## 许可证

仓库代码采用 [MIT 许可证](./LICENSE)。各软件包的许可由其自身的 `meta.license` 指定；百度网盘和嘉立创EDA专业版为非自由软件。

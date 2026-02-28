# 4个PR合4为1操作说明

你说得对：GitHub 页面上确实有 4 个开放 PR。

之前环境里看不到 `remote`，不代表 PR 不存在；只是本地仓库没有配置远程引用。因此脚本已升级为两种模式：

1. **ref 模式**：直接传 4 个本地/远程 git 引用
2. **PR 模式**：直接传 `owner/repo` 和 4 个 PR 编号，脚本会从 GitHub 拉取对应 PR head 后整合

## 用法

### 模式1：直接传 4 个引用

```bash
./merge_4_prs.sh <ref1> <ref2> <ref3> <ref4>
```

### 模式2：传 GitHub 仓库与 PR 编号（推荐）

```bash
./merge_4_prs.sh --repo adamliu123456/HappySocialGame --prs 1,2,3,4
```

> 如果你的仓库是私有仓库，请先确保本机 git 凭据可访问该仓库。

## 整合逻辑

1. 校验输入（4个 ref 或 4个 PR 号）。
2. 从基线分支（默认当前分支）创建整合分支。
3. 依次 `git merge --squash` 每个来源并形成中间提交（便于定位问题）。
4. 最后 `git reset --soft` 压成一个最终提交，得到真正的“合4为1”。

## 常用参数

- `--base <branch>`：指定基线分支
- `--branch <name>`：指定输出整合分支名
- `--final-message <msg>`：指定最终提交信息

#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
用法（两种模式）：

1) 直接传 4 个 git 引用（本地分支/远程分支/commit 都可）
   ./merge_4_prs.sh <ref1> <ref2> <ref3> <ref4>

2) 传 GitHub 仓库 + 4 个 PR 编号（即使本地没有 remote 也可）
   ./merge_4_prs.sh --repo <owner/repo> --prs <n1,n2,n3,n4>

可选参数：
  --base <branch>          指定整合基线分支（默认：当前分支）
  --branch <name>          指定输出分支名（默认：integration/4pr-时间戳）
  --final-message <msg>    指定最终单提交的 commit message
  -h, --help               查看帮助

示例：
  ./merge_4_prs.sh main feature/a feature/b feature/c
  ./merge_4_prs.sh --repo adamliu123456/HappySocialGame --prs 1,2,3,4
USAGE
}

err() {
  echo "错误: $*" >&2
  exit 1
}

mode=""
base_branch="$(git rev-parse --abbrev-ref HEAD)"
integration_branch="integration/4pr-$(date +%Y%m%d-%H%M%S)"
final_message="feat: consolidate strengths from 4 PRs into one cohesive change"
repo=""
prs_csv=""

args=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="${2:-}"
      shift 2
      ;;
    --prs)
      prs_csv="${2:-}"
      shift 2
      ;;
    --base)
      base_branch="${2:-}"
      shift 2
      ;;
    --branch)
      integration_branch="${2:-}"
      shift 2
      ;;
    --final-message)
      final_message="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      args+=("$1")
      shift
      ;;
  esac
done

if [[ -n "$repo" || -n "$prs_csv" ]]; then
  mode="prs"
  [[ -n "$repo" ]] || err "使用 --prs 时必须同时提供 --repo <owner/repo>"
  [[ -n "$prs_csv" ]] || err "使用 --repo 时必须同时提供 --prs <n1,n2,n3,n4>"
else
  mode="refs"
fi

refs=()

if [[ "$mode" == "refs" ]]; then
  [[ ${#args[@]} -eq 4 ]] || {
    usage
    err "ref 模式需要正好 4 个位置参数"
  }

  refs=("${args[@]}")
  for ref in "${refs[@]}"; do
    git rev-parse --verify --quiet "$ref" >/dev/null || err "找不到引用: $ref"
  done
else
  IFS=',' read -r -a pr_numbers <<<"$prs_csv"
  [[ ${#pr_numbers[@]} -eq 4 ]] || err "--prs 需要正好 4 个 PR 编号，用逗号分隔"

  for n in "${pr_numbers[@]}"; do
    [[ "$n" =~ ^[0-9]+$ ]] || err "PR 编号必须是数字: $n"
  done

  for n in "${pr_numbers[@]}"; do
    local_ref="pr-${n}-$(date +%s)-$RANDOM"
    fetch_url="https://github.com/${repo}.git"
    echo "拉取 PR #$n -> $local_ref"
    git fetch "$fetch_url" "pull/${n}/head:${local_ref}" >/dev/null
    refs+=("$local_ref")
  done
fi

git rev-parse --verify --quiet "$base_branch" >/dev/null || err "基线分支不存在: $base_branch"

echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
echo "基线分支: $base_branch"
echo "创建整合分支: $integration_branch"
git checkout -b "$integration_branch" "$base_branch" >/dev/null

for ref in "${refs[@]}"; do
  echo "=== 整合 $ref (squash) ==="
  git merge --squash "$ref" >/dev/null
  git commit -m "chore(integration): extract best parts from $ref" >/dev/null
done

echo "=== 压缩为最终单提交 ==="
merge_base="$(git merge-base "$base_branch" HEAD)"
git reset --soft "$merge_base"
git commit -m "$final_message" >/dev/null

if [[ "$mode" == "prs" ]]; then
  for ref in "${refs[@]}"; do
    git branch -D "$ref" >/dev/null 2>&1 || true
  done
fi

echo "完成。输出分支: $integration_branch"
echo "最终提交: $(git rev-parse --short HEAD)"

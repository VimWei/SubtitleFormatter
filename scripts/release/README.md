# 版本发布工具

## 功能描述
自动化版本发布流程，包括版本号更新、changelog更新、git提交和标签创建。

## 使用方法

### 通过脚本管理器（推荐）
```bash
uv run python scripts_manager.py release [bump_type]
```

### 直接运行
```bash
uv run python scripts/release/main.py [bump_type]
```

## 参数说明
- `bump_type`: 版本更新类型，可选值：
  - `patch`: 补丁版本 (默认)
  - `minor`: 次要版本
  - `major`: 主要版本
  - `alpha`: Alpha预发布
  - `beta`: Beta预发布
  - `rc`: 发布候选
  - `dev`: 开发版本

## 功能特性
- 自动版本号更新
- 更新changelog.md
- 运行测试和代码质量检查
- 创建git提交和标签
- 推送到远程仓库

## 依赖
- tomli-w >= 1.0.0

## 示例
```bash
# 补丁版本发布
uv run python scripts_manager.py release patch

# 次要版本发布
uv run python scripts_manager.py release minor
```

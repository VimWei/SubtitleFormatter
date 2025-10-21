# SubtitleFormatter 脚本使用指南

> **用户使用指南** - 如何运行和使用 SubtitleFormatter 的脚本工具

## 🚀 快速开始

### 基本命令
```bash
# 列出所有脚本
uv run python scripts_manager.py list

# 运行脚本（推荐方式）
uv run python scripts_manager.py <script_name> <arguments>

# 直接运行脚本
uv run python scripts/<script_path> <arguments>

# 显示帮助
uv run python scripts_manager.py help <script_name>
```

## 📋 可用脚本

### 1. 文本差异检测 (text-diff)
**功能**: 比较两个文本文件，识别词汇差异（忽略格式化差异）

**使用方法**:
```bash
# 方式1：通过脚本管理器（推荐）
uv run python scripts_manager.py text-diff <old_file> <new_file>
uv run python scripts_manager.py text-diff <old_file> <new_file> --json --html --csv
uv run python scripts_manager.py text-diff <old_file> <new_file> --output result.json

# 方式2：直接运行脚本
uv run python scripts/text_diff/main.py <old_file> <new_file>
uv run python scripts/text_diff/main.py <old_file> <new_file> --json --html --csv
uv run python scripts/text_diff/main.py <old_file> <new_file> --output-dir data/output
```

**注意**: 文件在data/input/目录中可直接使用文件名（仅限脚本管理器方式）

### 2. VTT文件清理 (clean-vtt)
**功能**: 清理和格式化VTT字幕文件

**使用方法**:
```bash
# 方式1：通过脚本管理器（推荐）
uv run python scripts_manager.py clean-vtt <input_file>

# 方式2：直接运行脚本
uv run python scripts/clean_vtt.py <input_file>
```

**注意**: 文件在data/input/目录中可直接使用文件名（仅限脚本管理器方式）

### 3. 字幕格式转换 (transcript-converter)
**功能**: 将非标准格式转换为SRT格式

**使用方法**:
```bash
# 方式1：通过脚本管理器（推荐）
uv run python scripts_manager.py transcript-converter <input_file>

# 方式2：直接运行脚本
uv run python scripts/transcript_converter/transcript_converter.py <input_file>
```

**注意**: 文件在data/input/目录中可直接使用文件名（仅限脚本管理器方式）

### 4. SRT重分段 (srt-resegment)
**功能**: 基于JSON时间戳重新分段SRT文件

**使用方法**:
```bash
# 方式1：通过脚本管理器（推荐）
uv run python scripts_manager.py srt-resegment <json_file> <srt_file>

# 方式2：直接运行脚本
uv run python scripts/srt-resegment-by-json.py <json_file> <srt_file>
```

**注意**: 文件在data/input/目录中可直接使用文件名（仅限脚本管理器方式）

### 5. 版本发布 (release)
**功能**: 自动化版本发布流程

**使用方法**:
```bash
# 方式1：通过脚本管理器（推荐）
uv run python scripts_manager.py release [bump_type]

# 方式2：直接运行脚本
uv run python scripts/release.py [bump_type]
```

**注意**: 两种方式功能完全相同

## 🔧 环境管理

### 依赖管理
每个脚本都有独立的依赖组，在 `pyproject.toml` 中定义：

```toml
[dependency-groups]
diff = ["colorama>=0.4.4", "rich>=13.0.0", "click>=8.0.0"]
clean-vtt = ["pandas>=1.5.0"]
release = ["tomli-w>=1.0.0"]
```

### 安装依赖
```bash
# 安装所有依赖
uv sync

# 安装特定脚本依赖
uv pip install --group diff
uv pip install --group clean-vtt
uv pip install --group release

# 通过脚本管理器安装
uv run python scripts_manager.py install diff
```

## 📁 路径处理

### 默认路径
脚本管理器支持默认路径，简化文件操作：

- **输入文件**: 默认从 `data/input/` 读取
- **输出文件**: 默认保存到 `data/output/`

### 使用示例
```bash
# 如果文件在 data/input/ 中，可以直接使用文件名
uv run python scripts_manager.py diff old.txt new.txt

# 脚本会自动转换为完整路径
# old.txt -> data/input/old.txt
# new.txt -> data/input/new.txt
```

### 路径规则
1. **相对路径**: 如果文件不在 `data/input/` 中，使用完整路径
2. **绝对路径**: 直接使用完整路径
3. **输出路径**: 如果输出文件没有路径，自动保存到 `data/output/`

## 🛠️ 故障排除

### 常见问题

1. **脚本找不到**
   ```bash
   # 检查脚本是否注册
   uv run python scripts_manager.py list
   ```

2. **依赖问题**
   ```bash
   # 安装脚本依赖
   uv run python scripts_manager.py install <script_name>
   
   # 或手动安装
   uv pip install --group <script_name>
   ```

3. **文件找不到**
   ```bash
   # 使用完整路径
   uv run python scripts_manager.py diff /full/path/old.txt /full/path/new.txt
   ```

### 调试命令
```bash
# 检查环境
uv run python --version
uv run pip list

# 检查脚本
uv run python scripts_manager.py list
uv run python scripts_manager.py help diff
```

## 🎯 实际使用示例

### 文本差异检测工作流
```bash
# 1. 准备文件
# 将 old.txt 和 new.txt 放在 data/input/ 目录下

# 2. 运行差异检测
uv run python scripts_manager.py diff old.txt new.txt --json

# 3. 查看结果
# - 控制台显示差异统计
# - 生成 JSON 报告到 data/output/
# - 可选：生成 HTML 和 CSV 报告
```

### 批量处理
```bash
# 处理多个文件对（文件在data/input/目录中）
for file in old_*.txt; do
    new_file="new_$(basename $file)"
    uv run python scripts_manager.py diff "$file" "$new_file" --json
done
```

## 📊 性能优化

### 大文件处理
```bash
# 对于大文件，可以添加更多上下文
uv run python scripts_manager.py diff large_old.txt large_new.txt --json --context 5
```

### 内存优化
```bash
# 对于内存敏感的场景，可以调整批处理大小
uv run python scripts_manager.py diff old.txt new.txt --json --batch-size 1000
```

## 📚 更多信息

### 开发者文档
如果你需要开发新脚本或了解脚本的内部实现，请参考：
- [scripts/README.md](../scripts/README.md) - 脚本开发指南
- [项目主文档](../README.md) - 核心程序使用说明

## 🎉 总结

通过这个指南，你可以：

1. **快速上手**: 使用 `uv run python scripts_manager.py` 运行脚本
2. **环境管理**: 通过 `uv sync` 和依赖组管理依赖
3. **路径处理**: 利用默认路径简化文件操作
4. **故障排除**: 解决常见的环境问题

**推荐工作流**:
```bash
# 1. 安装环境
uv sync

# 2. 列出脚本
uv run python scripts_manager.py list

# 3. 运行脚本
uv run python scripts_manager.py diff old.txt new.txt --json

# 4. 查看结果
# 检查 data/output/ 目录中的报告文件
```

这样你就可以充分利用 SubtitleFormatter 的脚本功能了！

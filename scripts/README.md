# SubtitleFormatter Scripts 开发规范

> **开发者文档** - 如何开发和管理 SubtitleFormatter 的脚本工具

## 📁 脚本目录结构

每个脚本应该组织为独立的目录：

```
scripts/
├── your_script/                    # 脚本目录
│   ├── main.py                    # 主程序文件（统一命名）
│   ├── README.md                  # 脚本使用说明
│   └── tests/                     # 测试文件（可选）
```

## 🔧 开发规范

### 1. 命名规范
- **目录名**: 使用小写字母和下划线，体现主要功能
- **主程序**: 统一命名为 `main.py`
- **脚本名**: 在 `scripts_manager.py` 中注册时使用短横线分隔

### 2. 入口文件规范
- 主程序文件应该可以直接运行
- 支持 `--help` 参数显示帮助信息
- 适当的错误处理和退出码

### 3. 注册新脚本
在 `scripts_manager.py` 的 `_load_registry()` 方法中添加新脚本：

```python
"your-script": {
    "path": "your_script/main.py",
    "description": "脚本功能描述",
    "dependency_group": "your-deps",  # 可选，无依赖则为 None
    "usage": "scripts_manager.py your-script <args>",
    "examples": [
        "scripts_manager.py your-script example.txt"
    ],
    "category": "your_category"
}
```

### 4. 依赖管理
在 `pyproject.toml` 的 `[dependency-groups]` 中定义脚本依赖：

```toml
[dependency-groups]
your-deps = [
    "package1>=1.0.0",
    "package2>=2.0.0",
]
```

### 5. 文档规范
每个脚本目录必须包含 `README.md`，说明：
- 脚本功能
- 使用方法
- 参数说明
- 示例

## 📋 开发示例

### 创建新脚本目录
```bash
mkdir scripts/my_new_script
touch scripts/my_new_script/main.py
touch scripts/my_new_script/README.md
```

### 脚本模板
```python
#!/usr/bin/env python3
"""脚本功能描述"""

import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description="脚本功能描述")
    parser.add_argument("input", help="输入文件")
    parser.add_argument("-o", "--output", help="输出文件")
    
    args = parser.parse_args()
    
    # 脚本逻辑
    print(f"处理文件: {args.input}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 🎯 最佳实践

1. **单一职责**: 每个脚本专注一个功能
2. **用户友好**: 提供清晰的帮助信息和错误提示
3. **路径处理**: 支持相对路径和绝对路径
4. **错误处理**: 适当的异常处理和退出码
5. **文档完整**: 提供详细的使用说明

## 📚 用户文档

用户使用脚本请参考：
- [docs/scripts_guide.md](../docs/scripts_guide.md) - 脚本使用指南
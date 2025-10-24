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

### 5. 默认路径处理规范
脚本管理器支持智能默认路径，简化文件操作：

#### 输入文件处理
- **自动检测**: 如果文件在 `data/input/` 目录中，只需提供文件名
- **完整路径**: 如果文件在其他位置，使用完整路径
- **自动创建**: 如果 `data/input/` 目录不存在，会自动创建

#### 输出文件处理
- **自动输出**: 大多数脚本会自动将输出保存到 `data/output/` 目录
- **智能命名**: 根据输入文件名自动生成输出文件名
- **目录创建**: 如果 `data/output/` 目录不存在，会自动创建

#### 实现示例
```python
def resolve_input_path(filename):
    """解析输入文件路径，支持默认路径处理"""
    if os.path.exists(filename):
        return filename  # 完整路径或当前目录文件
    
    # 尝试在默认输入目录中查找
    default_path = os.path.join("data", "input", filename)
    if os.path.exists(default_path):
        return default_path
    
    # 创建默认目录并返回路径
    os.makedirs("data/input", exist_ok=True)
    return default_path

def resolve_output_path(input_path, output_filename=None):
    """解析输出文件路径，支持默认路径处理"""
    if output_filename:
        return os.path.join("data", "output", output_filename)
    
    # 根据输入文件名生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join("data", "output", f"{base_name}_processed.txt")
```

### 6. 文档规范
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

### 默认路径处理示例

#### 用户使用场景
```bash
# 场景1: 文件在默认输入目录中
echo "test content" > data/input/test.txt
scripts_manager.py my-script test.txt
# 输出: data/output/test_processed.txt

# 场景2: 文件在其他位置
scripts_manager.py my-script /path/to/file.txt
# 输出: data/output/file_processed.txt

# 场景3: 指定输出文件名
scripts_manager.py my-script test.txt -o custom_output.txt
# 输出: data/output/custom_output.txt
```

#### 目录结构自动创建
```
project_root/
├── data/                    # 自动创建
│   ├── input/              # 自动创建
│   │   └── test.txt
│   └── output/             # 自动创建
│       └── test_processed.txt
└── scripts/
    └── my_new_script/
        └── main.py
```

### 脚本模板
```python
#!/usr/bin/env python3
"""脚本功能描述"""

import argparse
import os
import sys

def resolve_input_path(filename):
    """解析输入文件路径，支持默认路径处理"""
    if os.path.exists(filename):
        return filename  # 完整路径或当前目录文件
    
    # 尝试在默认输入目录中查找
    default_path = os.path.join("data", "input", filename)
    if os.path.exists(default_path):
        return default_path
    
    # 创建默认目录并返回路径
    os.makedirs("data/input", exist_ok=True)
    return default_path

def resolve_output_path(input_path, output_filename=None):
    """解析输出文件路径，支持默认路径处理"""
    if output_filename:
        return os.path.join("data", "output", output_filename)
    
    # 根据输入文件名生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join("data", "output", f"{base_name}_processed.txt")

def main():
    parser = argparse.ArgumentParser(description="脚本功能描述")
    parser.add_argument("input", help="输入文件（支持默认路径）")
    parser.add_argument("-o", "--output", help="输出文件（可选，默认自动生成）")
    
    args = parser.parse_args()
    
    # 解析路径
    input_path = resolve_input_path(args.input)
    output_path = resolve_output_path(input_path, args.output)
    
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 脚本逻辑
    print(f"处理文件: {input_path}")
    print(f"输出文件: {output_path}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 🎯 最佳实践

1. **单一职责**: 每个脚本专注一个功能
2. **用户友好**: 提供清晰的帮助信息和错误提示
3. **智能路径处理**: 实现默认路径处理，简化用户操作
   - 支持 `data/input/` 和 `data/output/` 默认目录
   - 自动创建必要的目录结构
   - 提供路径解析的便利函数
4. **错误处理**: 适当的异常处理和退出码
5. **文档完整**: 提供详细的使用说明

## 📚 用户文档

用户使用脚本请参考：
- [docs/scripts_guide.md](../docs/scripts_guide.md) - 脚本使用指南
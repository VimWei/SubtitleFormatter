# 使用指南

## 快速开始

1. 准备配置文件 `config.yaml`：
```yaml
max_width: 78
language: en
model_size: sm
input_file: data/input.txt
output_file: data/output-{timestamp}.txt
debug:
  enabled: true
  temp_dir: temp
```

2. 运行程序：
```bash
python main.py
```

## 配置方式

程序支持两种配置方式：配置文件和命令行参数。命令行参数的优先级高于配置文件。

### 1. 使用配置文件

在项目根目录创建 `config.yaml` 文件，包含所需的配置项。

使用默认配置文件运行：
```bash
python main.py
```

使用自定义配置文件：
```bash
python main.py -c my_config.yaml
```

### 2. 使用命令行参数

```bash
python main.py [选项]
```

可用参数：
- `--input`, `-i`: 输入文件路径
- `--output`, `-o`: 输出文件路径
- `--max-width`, `-w`: 最大行宽（默认：78）
- `--language`, `-l`: 文本语言（默认：en）
- `--model`, `-m`: 语言模型大小（sm/md/lg，默认：sm）
- `--config`, `-c`: 配置文件路径（默认：config.yaml）


## 使用建议

1. 语言模型选择
   - 小型模型 (sm): 快速处理，适合一般用途
   - 中型模型 (md): 平衡性能和准确性
   - 大型模型 (lg): 最高准确性，但加载较慢

2. 调试模式
   - 开发测试时建议启用
   - 生产环境建议禁用
   - 注意调试文件的存储空间

3. 最佳实践
   - 使用 UTF-8 编码的文本文件
   - 为输出文件使用时间戳避免覆盖
   - 根据实际需求选择合适的行宽 
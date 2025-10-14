# 配置说明

## 配置文件结构

可以通过创建 `config.yaml` 文件来设置默认参数：

```yaml
# 文本处理配置
max_width: 78        # 最大行宽
language: en         # 语言设置：'en' 或 'zh'
model_size: sm       # 模型大小：'sm', 'md' 或 'lg'

# 文件路径配置
input_file: data/input.txt
output_file: data/output-{timestamp}.txt  # 支持时间戳变量

# 调试配置
debug:
  enabled: true      # 是否启用调试输出
  temp_dir: temp     # 调试文件输出目录
```

## 参数说明

### 文本处理参数

- `max_width`
  - 说明：控制每行的最大字符数
  - 默认值：78
  - 建议范围：60-120
  - 注意：过小的值可能影响阅读体验，过大的值可能导致显示问题

- `language`
  - 说明：设置文本语言
  - 可选值：
    - `en`：英文（默认）
    - `zh`：中文
  - 注意：影响模型选择和语言处理策略

- `model_size`
  - 说明：spaCy 语言模型的大小
  - 可选值：
    - `sm`：小型模型（默认），约 12MB
    - `md`：中型模型，约 40MB
    - `lg`：大型模型，约 140MB
  - 注意：更大的模型通常提供更好的准确性，但加载更慢且消耗更多内存

### 文件路径配置

- `input_file`
  - 说明：输入文件路径
  - 支持相对路径和绝对路径
  - 必须使用 UTF-8 编码

- `output_file`
  - 说明：输出文件路径
  - 支持使用 `{timestamp}` 变量
  - 示例：`output-{timestamp}.txt` 将生成如 `output-20240101123456.txt` 的文件名

### 调试配置

- `debug.enabled`
  - 说明：是否启用调试输出
  - 可选值：`true` / `false`
  - 启用后会在每个处理步骤生成详细的调试信息

- `debug.temp_dir`
  - 说明：调试文件的输出目录
  - 默认值：`temp`
  - 每个处理步骤的结果都会保存在此目录下

## 配置文件优先级

1. 命令行参数（最高优先级）
2. 自定义配置文件中的设置
3. 默认配置值（最低优先级）

## 配置最佳实践

1. 总是指定 `language` 参数以获得最佳处理效果
2. 根据实际需求选择合适的 `model_size`
3. 开发调试时启用 `debug` 配置
4. 生产环境建议禁用调试输出
5. 使用 `{timestamp}` 避免文件覆盖 
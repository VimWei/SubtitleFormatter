# Smart Text Formatter

Smart Text Formatter 是一个智能文本格式化工具，它能够进行智能断句、清理文本、处理停顿词并进行智能断行，使文本更加易读。

## 主要功能

1. 基础文本清理：统一空白字符、处理空行
2. 智能断句：使用语言模型进行智能断句
3. 停顿词处理：识别和处理文本中的停顿词
4. 智能断行：基于语法结构进行智能断行
5. 自定义：支持自定义最大行宽、多语言支持、详细的调试输出支持

## 技术栈

- **Python**: 3.8.1+
- **环境管理**: [uv](https://docs.astral.sh/uv/) - 快速的 Python 包管理器
- **NLP 处理**: [spaCy](https://spacy.io/) - 自然语言处理库
- **配置管理**: [PyYAML](https://pyyaml.org/) - YAML 配置文件解析

## 安装要求

1. 确保已安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：
   ```bash
   # Windows (PowerShell)
   irm https://astral.sh/uv/install.ps1 | iex
   
   # macOS/Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. 安装依赖并创建虚拟环境：
   ```bash
   uv sync
   ```

3. 注意事项：
   - 首次运行时，程序会自动下载 spaCy 语言模型
   - 语言模型（如 en_core_web_md）约 50-100MB
   - 模型缓存位置：`~/.local/share/spacy/` 或 `%APPDATA%\spacy\` (Windows)
   - 确保有足够的磁盘空间（至少 200MB）和稳定的网络连接

## 使用方法

1. 运行程序：
   ```bash
   uv run python main.py
   ```

2. 程序将根据 `config.yaml` 中的配置处理文本文件

3. 输出文件将保存在 `data/output/` 目录下

## 文档

- [使用指南](docs/usage.md)
- [配置说明](docs/configuration.md)
- [开发指南](docs/development.md)

## License

This project is licensed under the **GNU General Public License v3.0 (GPL-3.0)**. 

This means:
- You are free to use, modify, and distribute this software
- Any derivative works must also be licensed under GPL-3.0
- You must make the source code available when distributing the software
- You must preserve copyright notices and license information

For more details, see the [LICENSE](LICENSE) file or visit [https://www.gnu.org/licenses/gpl-3.0.html](https://www.gnu.org/licenses/gpl-3.0.html).

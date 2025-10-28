# 插件开发指南

## 📋 概述

本文档为 SubtitleFormatter 插件开发提供详细的开发规范、实现示例和使用指南，帮助开发者快速创建和集成自定义插件。

**文档定位**: 本文档专注于**开发指南**，包括目录结构、配置文件、实现示例、安装使用等。核心架构设计请参考 [插件架构设计文档](plugin_architecture_design.md)，实施计划请参考 [主重构计划](src_refactor_plan.md)。

## 🎯 开发目标

### 核心目标
- **简单易用**: 最小化的开发门槛
- **标准化**: 统一的开发规范和接口
- **可扩展**: 支持各种类型的文本处理功能
- **独立开发**: 插件可以独立开发和测试

## 📁 插件目录结构

### 灵活的命名空间结构
```
SubtitleFormatter/
├── plugins/                          # 统一插件目录
│   ├── builtin/                      # 内置插件 (分类方式)
│   │   ├── text_cleaning/           # 插件目录 (下划线)
│   │   │   ├── plugin.json
│   │   │   ├── plugin.py
│   │   │   └── README.md
│   │   ├── punctuation_adder/       # 插件目录 (下划线)
│   │   ├── text_to_sentences/       # 插件目录 (下划线)
│   │   └── sentence_splitter/      # 插件目录 (下划线)
│   ├── examples/                     # 示例插件 (分类方式)
│   │   ├── simple_uppercase/        # 插件目录 (下划线)
│   │   └── word_counter/            # 插件目录 (下划线)
│   ├── community/                    # 社区插件 (分类方式)
│   │   ├── grammar_checker/         # 插件目录 (下划线)
│   │   └── style_optimizer/         # 插件目录 (下划线)
│   ├── username/                     # 个人插件 (来源方式)
│   │   ├── my_plugin1/              # 插件目录 (下划线)
│   │   └── my_plugin2/              # 插件目录 (下划线)
│   ├── experimental/                 # 实验性插件 (分类方式)
│   │   ├── ai_enhancer/             # 插件目录 (下划线)
│   │   └── voice_synthesis/         # 插件目录 (下划线)
│   └── deprecated/                   # 废弃插件 (分类方式)
│       ├── old_processor/           # 插件目录 (下划线)
│       └── legacy_converter/        # 插件目录 (下划线)
```

### 标准插件目录结构
```
namespace/plugin_name/
├── plugin.json          # 插件元数据 (必需)
├── plugin.py            # 插件主实现 (必需)
├── requirements.txt     # 依赖包 (可选)
└── README.md           # 说明文档 (可选)
```

### 目录说明
- **namespace**: 插件命名空间，可以是任意合法的目录名称
- **plugin_name**: 插件名称，使用下划线命名 (如 `text_cleaning`)
- **plugin.json**: 插件的基本信息和配置
- **plugin.py**: 插件的核心实现代码
- **requirements.txt**: 插件依赖的Python包
- **README.md**: 插件的使用说明和文档

### 命名空间组织方式
命名空间可以根据需要灵活组织，支持多种方式：

#### **按分类组织**
- `builtin/` - 内置插件
- `examples/` - 示例插件
- `community/` - 社区插件
- `experimental/` - 实验性插件
- `deprecated/` - 废弃插件

#### **按来源组织**
- `username/` - 个人开发者
- `organization/` - 组织/公司
- `github_user/` - GitHub 用户名

#### **按功能组织**
- `text_processing/` - 文本处理插件
- `audio_processing/` - 音频处理插件
- `format_conversion/` - 格式转换插件

#### **按状态组织**
- `stable/` - 稳定版本
- `beta/` - 测试版本
- `alpha/` - 开发版本

## 📝 命名规范

### 分层命名策略
SubtitleFormatter 采用分层命名策略，与现有的 scripts 系统保持一致：

#### 1. 文件系统层 (下划线)
- **目录名**: `text_cleaning`, `punctuation_adder`, `text_to_sentences`
- **文件名**: `plugin.py`, `main.py`, `README.md`
- **配置引用**: `subtitleformatter/text_cleaning`
- **变量名**: `plugin_name`, `input_data`

#### 2. 命令行层 (连字符)
- **CLI 命令**: `text-to-sentences`, `sentence-splitter`
- **帮助文档**: `scripts_manager.py text-to-sentences`
- **用户交互**: 保持易读性

#### 3. 映射机制
CLI 名称自动映射到文件路径：
- `text-to-sentences` → `text_to_sentences/main.py`
- `sentence-splitter` → `sentence_splitter/main.py`

### 命名空间规则
- **技术限制**: 使用合法的目录名称，避免特殊字符和空格
- **推荐约定**: 使用小写字母和下划线
- **组织自由**: 可以根据需要选择任意组织方式
- **引用格式**: 配置中使用 `namespace/plugin_name` 格式

### 插件名称规范
- 使用小写字母和下划线: `text_cleaning`, `punctuation_adder`
- 避免连字符和驼峰命名
- 名称应该描述性强且简洁
- 与现有 scripts 目录保持一致

## ⚙️ 插件配置文件

### plugin.json 格式
```json
{
    "name": "text_cleaning",
    "namespace": "builtin",
    "version": "1.0.0",
    "description": "文本清理插件 - 统一空白字符、换行符、标点符号",
    "author": "SubtitleFormatter Team",
    "input_type": "str",
    "output_type": "str",
    "enabled": true,
    "dependencies": [],
    "source": "builtin",
    "git_url": "https://github.com/subtitleformatter/text-cleaning.git"
}
```

### 配置字段说明
- **name**: 插件名称，使用下划线命名 (如 `text_cleaning`)
- **namespace**: 插件命名空间，可以是任意合法的目录名称 (如 `builtin`, `username`, `experimental`)
- **version**: 插件版本号
- **description**: 插件功能描述
- **author**: 插件作者
- **input_type**: 输入数据类型 (str, list, dict)
- **output_type**: 输出数据类型 (str, list, dict)
- **enabled**: 是否默认启用
- **dependencies**: 依赖的其他插件 (使用完整名称如 `builtin/text_cleaning`)
- **source**: 插件来源 (builtin, github, local)
- **git_url**: Git仓库地址（可选）

## 💻 插件实现

### 基础插件模板
```python
# plugin.py
from typing import Any
from ...plugins.base.plugin_base import TextProcessorPlugin

class TextCleaning(TextProcessorPlugin):
    """文本清理插件"""
    
    def get_input_type(self) -> type:
        """返回期望的输入数据类型"""
        return str
    
    def get_output_type(self) -> type:
        """返回输出的数据类型"""
        return str
    
    def process(self, input_data: str) -> str:
        """处理文本数据"""
        # 在这里实现你的处理逻辑
        # 移除多余空格
        cleaned = ' '.join(input_data.split())
        
        # 统一换行符
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        return cleaned
```

**详细接口定义**: 请参考 [插件架构设计文档](plugin_architecture_design.md#核心组件) 中的 `TextProcessorPlugin` 基类定义。

### 插件实现要点

#### 1. 继承基类
所有插件必须继承 `TextProcessorPlugin` 基类

#### 2. 实现必需方法
- `get_input_type()`: 定义输入数据类型
- `get_output_type()`: 定义输出数据类型
- `process()`: 实现核心处理逻辑

#### 3. 类型安全
确保输入输出类型与声明一致，系统会自动进行类型检查

## 🔧 插件默认值管理

### 正确的配置使用方式
插件子类应该直接使用 `self.config`，基类已经自动处理了默认配置的加载：

```python
def __init__(self, config: Dict[str, Any] = None):
    super().__init__(config)  # 基类自动加载默认配置
    
    # 正确：直接使用配置，基类已处理默认值
    self.enabled = self.config["enabled"]
    self.model_name = self.config["model_name"]
    self.capitalize_sentences = self.config["capitalize_sentences"]
    self.split_sentences = self.config["split_sentences"]
    self.replace_dashes = self.config["replace_dashes"]
    
    # 错误：不要再设置默认值
    # self.enabled = self.config.get("enabled", default_config.get("enabled", True))
```

### 基类职责
- 自动从 plugin.json 加载默认配置
- 将默认配置合并到 `self.config` 中
- 确保配置的完整性和一致性

### 插件子类职责
- 直接使用 `self.config["key"]`
- 信任基类已经处理了默认配置
- 专注于业务逻辑实现

### 配置优先级
1. **用户配置** (最高优先级)
2. **plugin.json 默认值** (中等优先级) 
3. **代码中的硬编码默认值** (最低优先级，仅作后备)

### 最佳实践
- **推荐**: 直接使用 `self.config["key"]`
- **避免**: 在 `__init__` 中再设置默认值
- **确保**: plugin.json 中的默认值与代码中的后备默认值一致

### 常见问题
**Q: 为什么不能直接在代码中硬编码默认值？**
A: 硬编码默认值会导致 GUI 的 "Reset to Defaults" 功能失效，因为 GUI 从 plugin.json 读取默认值，而插件使用硬编码值，造成不一致。

**Q: 如何确保配置的一致性？**
A: 使用基类的 `get_default_config_from_plugin_json()` 方法，确保所有默认值都来自 plugin.json 文件。

## 🔧 插件开发示例

### 示例1: 文本清理插件
```python
class TextCleaner(TextProcessorPlugin):
    """文本清理插件"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)  # 基类自动加载默认配置
        
        # 直接使用配置，基类已处理默认值
        self.enabled = self.config["enabled"]
        self.normalize_punctuation = self.config["normalize_punctuation"]
        self.normalize_numbers = self.config["normalize_numbers"]
        self.normalize_whitespace = self.config["normalize_whitespace"]
        self.clean_empty_lines = self.config["clean_empty_lines"]
        self.add_spaces_around_punctuation = self.config["add_spaces_around_punctuation"]
        self.remove_bom = self.config["remove_bom"]
    
    def get_input_type(self) -> type:
        """返回期望的输入数据类型"""
        return str
    
    def get_output_type(self) -> type:
        """返回输出的数据类型"""
        return str
    
    def process(self, input_data: str) -> str:
        """执行文本清理"""
        # 移除多余空格
        cleaned = ' '.join(input_data.split())
        
        # 统一换行符
        cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
        
        return cleaned
```

### 示例2: 句子分割插件
```python
class TextToSentences(TextProcessorPlugin):
    """句子分割插件"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)  # 基类自动加载默认配置
        
        # 直接使用配置，基类已处理默认值
        self.enabled = self.config["enabled"]
    
    def get_input_type(self) -> type:
        """返回期望的输入数据类型"""
        return str
    
    def get_output_type(self) -> type:
        """返回输出的数据类型"""
        return list
    
    def process(self, input_data: str) -> list:
        """执行句子分割"""
        import re
        
        # 简单的句子分割逻辑
        sentences = re.split(r'[.!?]+', input_data)
        
        # 清理空句子和多余空格
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
```

### 示例3: 带配置的插件
```python
class ConfigurablePlugin(TextProcessorPlugin):
    """可配置的插件示例"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)  # 基类自动加载默认配置
        
        # 直接使用配置，基类已处理默认值
        self.enabled = self.config["enabled"]
        self.max_length = self.config["max_length"]
        self.prefix = self.config["prefix"]
    
    def get_input_type(self) -> type:
        """返回期望的输入数据类型"""
        return str
    
    def get_output_type(self) -> type:
        """返回输出的数据类型"""
        return str
    
    def process(self, input_data: str) -> str:
        """根据配置处理文本"""
        # 添加前缀
        result = self.prefix + input_data
        
        # 限制长度
        if len(result) > self.max_length:
            result = result[:self.max_length] + "..."
        
        return result
```

## 📦 插件安装

### 安装方式

#### 1. 本地文件夹安装
```bash
# 将插件文件夹复制到对应的命名空间目录
cp -r my_plugin/ /path/to/SubtitleFormatter/plugins/username/
```

#### 2. Git 仓库安装
```bash
# 克隆到对应的命名空间目录
cd /path/to/SubtitleFormatter/plugins/username/
git clone https://github.com/username/subtitleformatter-my-plugin.git my_plugin
```

#### 3. ZIP 文件安装
```bash
# 解压到对应的命名空间目录
unzip my_plugin.zip -d /path/to/SubtitleFormatter/plugins/username/
```

### 命名空间规则
- **灵活组织**: 可以根据需要选择任意命名空间
- **推荐约定**: 
  - `builtin/` - 内置插件
  - `examples/` - 示例插件
  - `community/` - 社区插件
  - `username/` - 个人插件
  - `experimental/` - 实验性插件
- **自定义命名空间**: 可以使用任意合法的目录名称

### 安装验证
1. 确保插件目录在正确的命名空间下
2. 确保 `plugin.json` 文件存在且格式正确
3. 确保 `plugin.py` 文件存在且可导入
4. 重启应用或点击刷新按钮
5. 在插件列表中查看是否出现新插件

## 🔄 插件更新

### Git 仓库更新
```bash
cd /path/to/SubtitleFormatter/plugins/my_plugin/
git pull origin main
```

### 手动更新
1. 备份当前插件
2. 下载新版本
3. 替换插件文件
4. 重启应用

## 🧪 插件测试

### 单元测试示例
```python
import unittest
from my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def setUp(self):
        self.plugin = MyPlugin({"enabled": True})
    
    def test_input_output_types(self):
        """测试输入输出类型"""
        self.assertEqual(self.plugin.get_input_type(), str)
        self.assertEqual(self.plugin.get_output_type(), str)
    
    def test_process_function(self):
        """测试处理功能"""
        input_text = "hello world"
        result = self.plugin.process(input_text)
        self.assertEqual(result, "HELLO WORLD")
    
    def test_empty_input(self):
        """测试空输入"""
        result = self.plugin.process("")
        self.assertEqual(result, "")

if __name__ == '__main__':
    unittest.main()
```

### 集成测试
```python
# 在 SubtitleFormatter 中测试插件
from src.subtitleformatter.core.text_processor import TextProcessor

# 加载配置 - 使用完整的命名空间引用
config = {
    "plugins": {
        "order": ["builtin/my_plugin"],
        "builtin/my_plugin": {"enabled": True}
    }
}

# 创建处理器
processor = TextProcessor(config)

# 测试处理
result = processor.process("test input")
print(f"Result: {result}")
```

## 📋 开发检查清单

### 开发前检查
- [ ] 确定插件功能和输入输出类型
- [ ] 设计插件配置参数
- [ ] 准备测试数据

### 开发中检查
- [ ] 正确继承 `TextProcessorPlugin`
- [ ] 实现所有必需方法
- [ ] 确保类型安全
- [ ] 添加错误处理
- [ ] 编写单元测试

### 开发后检查
- [ ] 创建 `plugin.json` 配置文件
- [ ] 编写 `README.md` 文档
- [ ] 测试插件安装和运行
- [ ] 验证插件链集成
- [ ] 性能测试

## 🚨 常见问题

### Q: 插件无法加载
**A**: 检查以下几点：
1. `plugin.json` 文件是否存在且格式正确
2. `plugin.py` 文件是否存在且可导入
3. 插件类名是否正确
4. 依赖包是否已安装

### Q: 类型错误
**A**: 确保：
1. `get_input_type()` 和 `get_output_type()` 返回正确的类型
2. `process()` 方法的输入输出类型与声明一致
3. 插件链中前后插件的类型匹配

### Q: 配置不生效
**A**: 检查：
1. 配置参数名称是否正确
2. 配置值类型是否匹配
3. 插件是否正确读取配置

### Q: 性能问题
**A**: 优化建议：
1. 避免在 `process()` 方法中进行重复初始化
2. 使用缓存机制
3. 优化算法复杂度
4. 考虑异步处理

## 📚 相关文档

### 架构设计
详细的插件架构设计请参考：
**[插件架构设计文档](plugin_architecture_design.md)**

### GUI设计
插件管理界面设计请参考：
**[插件GUI设计文档](plugin_gui_design.md)**

### 主重构计划
整体重构计划请参考：
**[主重构计划文档](src_refactor_plan.md)**

## 🎯 总结

本开发指南提供了完整的插件开发流程：

1. **准备阶段**: 确定功能需求和设计
2. **开发阶段**: 实现插件核心逻辑
3. **测试阶段**: 单元测试和集成测试
4. **部署阶段**: 安装和配置插件
5. **维护阶段**: 更新和优化插件

通过遵循本指南，开发者可以快速创建高质量、可维护的插件，为 SubtitleFormatter 生态系统贡献力量。

---

**注意**: 本指南与插件架构设计文档和GUI设计文档配合使用，确保插件开发的完整性和一致性。

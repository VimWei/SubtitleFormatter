# 插件化架构设计文档

## 📋 概述

本文档详细描述了 SubtitleFormatter 的插件化架构设计，旨在解决当前线性串行处理流程的局限性，提供更灵活、可扩展的文本处理架构。

## 🎯 设计目标

### 核心目标
- **灵活性**: 支持自由组合和排序处理组件
- **可扩展性**: 轻松添加新功能而不影响现有组件
- **可维护性**: 清晰的职责分离和统一的接口规范
- **配置驱动**: 通过配置文件控制处理流程

### 解决的问题
- 当前线性串行流程无法灵活调整
- 新功能添加需要修改核心代码
- 组件间耦合度高，难以独立测试
- 无法根据需求动态调整处理流程

## 🏗️ 架构设计

### 1. 核心组件

#### 1.1 插件基类 (TextProcessorPlugin)
```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

class TextProcessorPlugin(ABC):
    """文本处理插件基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.name = self.__class__.__name__
    
    @abstractmethod
    def process(self, input_data: Any) -> Any:
        """处理输入数据并返回结果
        
        Args:
            input_data: 输入数据，类型由 get_input_type() 定义
            
        Returns:
            处理后的数据，类型由 get_output_type() 定义
        """
        pass
    
    @abstractmethod
    def get_input_type(self) -> type:
        """返回期望的输入数据类型
        
        Returns:
            输入数据的类型 (str, list, dict 等)
        """
        pass
    
    @abstractmethod
    def get_output_type(self) -> type:
        """返回输出的数据类型
        
        Returns:
            输出数据的类型 (str, list, dict 等)
        """
        pass
    
    def is_enabled(self) -> bool:
        """检查插件是否启用
        
        Returns:
            True 如果插件启用，False 否则
        """
        return self.config.get("enabled", True)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """获取插件配置
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
```

#### 1.2 插件管理器 (TextProcessor)
```python
class TextProcessor:
    """插件化文本处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.plugins: List[TextProcessorPlugin] = []
        self._load_plugins()
    
    def _load_plugins(self):
        """根据配置加载插件"""
        plugin_configs = self.config.get("plugins", {})
        
        # 按顺序加载插件
        plugin_order = plugin_configs.get("order", [
            "text_cleaning",
            "punctuation_adder", 
            "text_to_sentences",
            "sentence_splitter"
        ])
        
        for plugin_name in plugin_order:
            if plugin_configs.get(plugin_name, {}).get("enabled", True):
                plugin = self._create_plugin(plugin_name, plugin_configs[plugin_name])
                if plugin:
                    self.plugins.append(plugin)
    
    def _create_plugin(self, name: str, config: Dict[str, Any]) -> Optional[TextProcessorPlugin]:
        """创建插件实例"""
        plugin_map = {
            "text_cleaning": TextCleaner,
            "punctuation_adder": PunctuationAdder,
            "text_to_sentences": TextToSentences,
            "sentence_splitter": SentenceSplitter,
        }
        
        plugin_class = plugin_map.get(name)
        if plugin_class:
            return plugin_class(config)
        return None
    
    def process(self, input_text: str) -> Any:
        """执行插件链处理
        
        Args:
            input_text: 输入文本
            
        Returns:
            处理后的结果
        """
        current_data = input_text
        
        for plugin in self.plugins:
            if not plugin.is_enabled():
                continue
                
            # 检查数据类型兼容性
            if not isinstance(current_data, plugin.get_input_type()):
                raise TypeError(
                    f"Plugin {plugin.name} expects {plugin.get_input_type()}, "
                    f"got {type(current_data)}"
                )
            
            # 执行插件处理
            current_data = plugin.process(current_data)
        
        return current_data
    
    def add_plugin(self, plugin: TextProcessorPlugin, position: Optional[int] = None):
        """动态添加插件
        
        Args:
            plugin: 要添加的插件
            position: 插入位置，None 表示添加到末尾
        """
        if position is None:
            self.plugins.append(plugin)
        else:
            self.plugins.insert(position, plugin)
    
    def remove_plugin(self, plugin_name: str):
        """移除插件
        
        Args:
            plugin_name: 要移除的插件名称
        """
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
    
    def get_plugin_chain(self) -> List[str]:
        """获取当前插件链
        
        Returns:
            启用的插件名称列表
        """
        return [p.name for p in self.plugins if p.is_enabled()]
    
    def get_plugin_by_name(self, name: str) -> Optional[TextProcessorPlugin]:
        """根据名称获取插件
        
        Args:
            name: 插件名称
            
        Returns:
            插件实例或 None
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None
```

### 2. 插件实现示例

#### 2.1 文本清理插件
```python
class TextCleaner(TextProcessorPlugin):
    """文本清理插件"""
    
    def get_input_type(self) -> type:
        return str
    
    def get_output_type(self) -> type:
        return str
    
    def process(self, input_data: str) -> str:
        """执行文本清理"""
        # 现有的文本清理逻辑
        cleaned_text, stats = self._clean_text(input_data)
        
        # 记录统计信息
        if hasattr(self, 'debug_output'):
            self.debug_output.show_step("文本清理", cleaned_text, stats)
        
        return cleaned_text
    
    def _clean_text(self, text: str) -> tuple[str, dict]:
        """实际的文本清理逻辑"""
        # 这里实现现有的 TextCleaner 逻辑
        pass
```

#### 2.2 标点恢复插件
```python
class PunctuationAdder(TextProcessorPlugin):
    """标点恢复插件"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.model = None
    
    def get_input_type(self) -> type:
        return str
    
    def get_output_type(self) -> type:
        return str
    
    def process(self, input_data: str) -> str:
        """执行标点恢复"""
        if self.model is None:
            self.model = self._load_model()
        
        punctuated_text = self.model.restore_punctuation(input_data)
        
        # 记录统计信息
        if hasattr(self, 'debug_output'):
            stats = {
                "text_length": len(input_data),
                "punctuation_count": self._count_punctuation(punctuated_text),
                "processing_time": self._get_processing_time()
            }
            self.debug_output.show_step("标点恢复", punctuated_text, stats)
        
        return punctuated_text
    
    def _load_model(self):
        """加载标点恢复模型"""
        # 使用 ModelManager 加载模型
        pass
```

#### 2.3 句子分割插件
```python
class TextToSentences(TextProcessorPlugin):
    """句子分割插件"""
    
    def get_input_type(self) -> type:
        return str
    
    def get_output_type(self) -> type:
        return list
    
    def process(self, input_data: str) -> List[str]:
        """执行句子分割"""
        sentences = self._split_sentences(input_data)
        
        # 记录统计信息
        if hasattr(self, 'debug_output'):
            stats = {
                "sentence_count": len(sentences),
                "avg_sentence_length": sum(len(s) for s in sentences) / len(sentences) if sentences else 0,
                "max_sentence_length": max(len(s) for s in sentences) if sentences else 0
            }
            self.debug_output.show_step("句子分割", sentences, stats)
        
        return sentences
    
    def _split_sentences(self, text: str) -> List[str]:
        """实际的句子分割逻辑"""
        # 这里实现现有的 text_to_sentences 逻辑
        pass
```

#### 2.4 句子拆分插件
```python
class SentenceSplitter(TextProcessorPlugin):
    """句子拆分插件"""
    
    def get_input_type(self) -> type:
        return list
    
    def get_output_type(self) -> type:
        return list
    
    def process(self, input_data: List[str]) -> List[str]:
        """执行句子拆分"""
        split_sentences = self._split_long_sentences(input_data)
        
        # 记录统计信息
        if hasattr(self, 'debug_output'):
            stats = {
                "original_sentences": len(input_data),
                "split_sentences": len(split_sentences),
                "split_ratio": (len(split_sentences) - len(input_data)) / len(input_data) * 100 if input_data else 0
            }
            self.debug_output.show_step("句子拆分", split_sentences, stats)
        
        return split_sentences
    
    def _split_long_sentences(self, sentences: List[str]) -> List[str]:
        """实际的句子拆分逻辑"""
        # 这里实现现有的 sentence_splitter 逻辑
        pass
```

## ⚙️ 配置系统

### 1. 配置文件结构
```toml
# 插件化配置结构
[plugins]
# 插件执行顺序
order = ["text_cleaning", "punctuation_adder", "text_to_sentences", "sentence_splitter"]

# 文本清理插件
[plugins.text_cleaning]
enabled = true
# 保留现有配置

# 标点恢复插件
[plugins.punctuation_adder]
enabled = true
model_name = "oliverguhr/fullstop-punctuation-multilang-large"
local_models_dir = "models/"

# 句子分割插件
[plugins.text_to_sentences]
enabled = true
# 无额外配置

# 句子拆分插件
[plugins.sentence_splitter]
enabled = true
min_recursive_length = 70
max_depth = 8

# 未来可扩展的插件示例
[plugins.future_plugin]
enabled = false
# 新功能配置
```

### 2. 配置验证
```python
class ConfigValidator:
    """配置验证器"""
    
    @staticmethod
    def validate_plugin_config(config: Dict[str, Any]) -> bool:
        """验证插件配置"""
        required_keys = ["plugins"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"Missing required config key: {key}")
        
        plugins_config = config["plugins"]
        if "order" not in plugins_config:
            raise ValueError("Missing plugin order configuration")
        
        return True
```

## 🔧 使用示例

### 1. 基本使用
```python
# 加载配置
config = load_config("config.toml")

# 创建处理器
processor = TextProcessor(config)

# 处理文本
result = processor.process("Hello world this is a test")

# 获取插件链
chain = processor.get_plugin_chain()
print(f"Processing chain: {' → '.join(chain)}")
```

### 2. 动态调整
```python
# 动态添加插件
new_plugin = GrammarChecker({"enabled": True})
processor.add_plugin(new_plugin, position=2)

# 禁用特定插件
plugin = processor.get_plugin_by_name("punctuation_adder")
if plugin:
    plugin.config["enabled"] = False

# 重新处理
result = processor.process("New text to process")
```

### 3. 自定义插件
```python
class CustomPlugin(TextProcessorPlugin):
    """自定义插件示例"""
    
    def get_input_type(self) -> type:
        return str
    
    def get_output_type(self) -> type:
        return str
    
    def process(self, input_data: str) -> str:
        # 自定义处理逻辑
        return input_data.upper()

# 注册自定义插件
processor._create_plugin = lambda name, config: CustomPlugin(config) if name == "custom" else None
```

## 🚀 扩展性设计

### 1. 插件类型分类

#### 文本处理插件
- **GrammarChecker**: 语法检查插件
- **StyleOptimizer**: 文体优化插件
- **TranslationPlugin**: 翻译插件
- **SummarizationPlugin**: 摘要生成插件

#### 格式处理插件
- **MarkdownFormatter**: Markdown格式化插件
- **HTMLFormatter**: HTML格式化插件
- **PDFGenerator**: PDF生成插件
- **SubtitleFormatter**: 字幕格式化插件

#### 质量控制插件
- **QualityChecker**: 质量检查插件
- **ConsistencyChecker**: 一致性检查插件
- **ReadabilityAnalyzer**: 可读性分析插件

### 2. 插件开发指南

#### 实现新插件
```python
class NewFeaturePlugin(TextProcessorPlugin):
    """新功能插件示例"""
    
    def get_input_type(self) -> type:
        return str  # 或 list, dict 等
    
    def get_output_type(self) -> type:
        return str  # 或 list, dict 等
    
    def process(self, input_data: Any) -> Any:
        # 实现具体功能
        return processed_data
```

#### 注册插件
```python
# 在 TextProcessor 中添加新插件
plugin_map = {
    "text_cleaning": TextCleaner,
    "punctuation_adder": PunctuationAdder,
    "text_to_sentences": TextToSentences,
    "sentence_splitter": SentenceSplitter,
    "new_feature": NewFeaturePlugin,  # 新增
}
```

#### 配置插件
```toml
[plugins.new_feature]
enabled = true
# 插件特定配置
param1 = "value1"
param2 = 42
```

## 📊 架构优势

### 1. 灵活性
- **自由组合**: 可以任意组合和排序插件
- **动态配置**: 通过配置文件控制插件启用/禁用
- **运行时调整**: 支持动态添加/移除插件

### 2. 可扩展性
- **新功能添加**: 只需实现新的插件类
- **向后兼容**: 现有插件不受新插件影响
- **独立开发**: 每个插件可以独立开发和测试

### 3. 可维护性
- **职责分离**: 每个插件只负责特定功能
- **接口统一**: 所有插件遵循相同的接口规范
- **类型安全**: 自动检查数据类型兼容性

### 4. 可测试性
- **单元测试**: 每个插件可以独立测试
- **集成测试**: 可以测试不同的插件组合
- **模拟测试**: 可以轻松模拟插件行为

## 🔄 架构演进路径

### 阶段1: 基础插件化
- 实现核心插件架构
- 迁移现有功能到插件
- 建立配置系统

### 阶段2: 功能扩展
- 添加新的文本处理插件
- 实现插件依赖管理
- 添加插件性能监控

### 阶段3: 高级特性
- 实现插件热插拔
- 添加插件版本管理
- 实现插件市场机制

## ⚠️ 注意事项

### 1. 性能考虑
- 插件链处理可能增加延迟
- 需要合理控制插件数量
- 考虑插件缓存机制

### 2. 错误处理
- 插件失败时的回退机制
- 错误传播和恢复策略
- 插件健康检查

### 3. 兼容性
- 保持现有接口兼容性
- 版本升级策略
- 配置迁移方案

---

**注意**: 此架构设计为 SubtitleFormatter 的核心架构，需要与主重构计划配合实施。

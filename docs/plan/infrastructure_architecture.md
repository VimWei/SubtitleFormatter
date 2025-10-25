# SubtitleFormatter 基础设施架构文档

## 📋 概述

本文档详细描述了 SubtitleFormatter 作为插件管理平台的核心基础设施组件，这些组件为插件生态系统提供了完整的运行环境和开发支持。

**文档定位**: 本文档专注于**基础设施架构**，包括现有组件、新增组件、集成机制等。核心架构设计请参考 [插件架构设计文档](plugin_architecture_design.md)，实施计划请参考 [主重构计划](src_refactor_plan.md)。

## 🎯 核心理念

SubtitleFormatter 的核心价值在于：
1. **提供完整的公共基础设施** - 让插件开发者专注于业务逻辑
2. **统一的插件管理平台** - 通过插件链配置实现灵活扩展
3. **标准化的开发环境** - 提供一致的开发体验

## 🏗️ 基础设施架构

### 完整架构图
```
SubtitleFormatter 插件管理平台
├── 核心基础设施
│   ├── UnifiedLogger (日志系统)
│   ├── DebugOutput (调试输出)
│   ├── ModelManager (模型管理)
│   ├── ConfigManager (配置管理)
│   └── VersionCheckService (版本管理)
├── GUI基础设施
│   ├── ThemeLoader (主题系统)
│   ├── MainWindow (主窗口)
│   └── LogPanel (日志面板)
├── 插件平台基础设施 (新增)
│   ├── PluginRegistry (插件注册表)
│   ├── PluginLifecycleManager (生命周期管理)
│   ├── PluginConfigManager (插件配置)
│   ├── PluginSandbox (安全沙箱)
│   ├── PluginEventSystem (事件系统)
│   └── PluginPerformanceMonitor (性能监控)
└── 文件系统管理
    ├── data/input/ (输入目录)
    ├── data/configs/ (配置目录)
    ├── models/ (模型目录)
    ├── plugins/ (插件目录)
    └── temp/ (临时目录)
```

## 🔧 现有基础设施组件

### 1. 日志系统 (`UnifiedLogger`)

**位置**: `src/subtitleformatter/utils/unified_logger.py`

**功能**:
- 统一管理终端输出和GUI日志面板
- 支持简洁模式和详细模式
- 自动添加时间戳和日志级别
- 提供类似print的简单使用方式

**核心特性**:
```python
class UnifiedLogger:
    """统一日志管理器，负责所有终端和GUI输出"""
    
    def log(self, message: str, level: str = "INFO") -> None:
        """统一的日志输出方法"""
        pass
    
    def set_debug_mode(self, enabled: bool = True) -> None:
        """设置调试模式，控制详细日志输出"""
        pass
    
    def step(self, step_name: str, message: str = "") -> None:
        """处理步骤日志"""
        pass
```

**插件使用方式**:
```python
from subtitleformatter.utils.unified_logger import logger

class MyPlugin(TextProcessorPlugin):
    def process(self, input_data: str) -> str:
        logger.info("开始处理文本")
        # 处理逻辑
        logger.step("处理完成", f"处理了 {len(input_data)} 个字符")
        return result
```

### 2. 调试输出系统 (`DebugOutput`)

**位置**: `src/subtitleformatter/utils/debug_output.py`

**功能**:
- 保存中间处理结果到文件
- 生成详细的调试报告
- 管理临时文件和输出目录
- 支持调试模式开关

**核心特性**:
```python
class DebugOutput:
    """调试输出和文件保存工具"""
    
    def show_step(self, step_name: str, data: Any, stats: dict = None):
        """显示处理步骤和统计信息"""
        pass
    
    def save_intermediate_result(self, filename: str, data: Any):
        """保存中间处理结果"""
        pass
    
    def generate_report(self) -> str:
        """生成调试报告"""
        pass
```

**插件使用方式**:
```python
class MyPlugin(TextProcessorPlugin):
    def process(self, input_data: str) -> str:
        # 处理逻辑
        result = self._process_text(input_data)
        
        # 记录调试信息
        if hasattr(self, 'debug_output'):
            stats = {
                "input_length": len(input_data),
                "output_length": len(result),
                "processing_time": self._get_processing_time()
            }
            self.debug_output.show_step("文本处理", result, stats)
        
        return result
```

### 3. 模型管理器 (`ModelManager`)

**位置**: `src/subtitleformatter/models/model_manager.py`

**功能**:
- 管理spaCy语言模型的下载和加载
- 支持离线模型使用
- 模型版本管理和缓存
- 自动模型下载和更新

**核心特性**:
```python
class ModelManager:
    """语言模型管理器"""
    
    @staticmethod
    def get_model(config: dict):
        """获取语言模型实例"""
        pass
    
    @staticmethod
    def download_model(model_name: str, models_dir: str):
        """下载模型到本地"""
        pass
    
    @staticmethod
    def get_punctuation_model(config: dict):
        """获取标点恢复模型实例 (新增)"""
        pass
```

**插件使用方式**:
```python
class PunctuationAdder(TextProcessorPlugin):
    def __init__(self, config: dict):
        super().__init__(config)
        self.model = None
    
    def process(self, input_data: str) -> str:
        if self.model is None:
            self.model = ModelManager.get_punctuation_model(self.config)
        
        return self.model.restore_punctuation(input_data)
```

### 4. 配置管理器 (`ConfigManager`)

**位置**: `src/subtitleformatter/config/config_manager.py`

**功能**:
- 加载默认和用户配置文件
- 配置标准化和验证
- 原子化配置保存
- 支持配置热更新

**核心特性**:
```python
class ConfigManager:
    """集中化配置管理器"""
    
    def load(self) -> Dict[str, Any]:
        """加载配置文件"""
        pass
    
    def save(self) -> None:
        """保存配置文件"""
        pass
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取配置值"""
        pass
    
    def set(self, key: str, value: Any) -> None:
        """设置配置值"""
        pass
```

**插件使用方式**:
```python
class MyPlugin(TextProcessorPlugin):
    def __init__(self, config: dict):
        super().__init__(config)
        self.max_length = config.get("max_length", 100)
        self.enabled = config.get("enabled", True)
```

### 5. 版本管理系统 (`VersionCheckService`)

**位置**: `src/subtitleformatter/services/version_check_service.py`

**功能**:
- 检查应用更新
- 版本比较和通知
- 更新信息展示
- 网络连接处理

**核心特性**:
```python
class VersionCheckService:
    """版本检查和更新服务"""
    
    def check_for_updates(self) -> Tuple[bool, str, Optional[str]]:
        """检查是否有新版本"""
        pass
    
    def get_latest_version(self) -> Optional[str]:
        """获取最新版本号"""
        pass
```

### 6. 主题系统 (`ThemeLoader`)

**位置**: `src/subtitleformatter/gui/styles/theme_loader.py`

**功能**:
- 加载GUI主题样式
- 界面美化管理
- 主题切换支持
- 样式一致性保证

**核心特性**:
```python
class ThemeLoader:
    """主题加载器"""
    
    def load_theme(self, theme_name: str) -> str:
        """加载指定主题"""
        pass
    
    def get_available_themes(self) -> List[str]:
        """获取可用主题列表"""
        pass
```

## 🚀 插件平台基础设施 (新增)

### 1. 插件注册表 (`PluginRegistry`)

**功能**:
- 插件发现和注册
- 插件元数据管理
- 插件依赖解析
- 插件版本管理

**设计**:
```python
class PluginRegistry:
    """插件注册表"""
    
    def __init__(self, plugin_dir: str = "plugins"):
        self.plugin_dir = Path(plugin_dir)
        self.plugins = {}
        self.dependencies = {}
    
    def scan_plugins(self) -> Dict[str, PluginInfo]:
        """扫描并注册所有插件"""
        pass
    
    def register_plugin(self, plugin_info: PluginInfo):
        """注册单个插件"""
        pass
    
    def resolve_dependencies(self, plugin_name: str) -> List[str]:
        """解析插件依赖关系"""
        pass
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """获取插件信息"""
        pass
```

### 2. 插件生命周期管理器 (`PluginLifecycleManager`)

**功能**:
- 插件加载/卸载
- 插件初始化/清理
- 插件状态监控
- 错误恢复机制

**设计**:
```python
class PluginLifecycleManager:
    """插件生命周期管理"""
    
    def load_plugin(self, plugin_name: str) -> bool:
        """加载插件"""
        pass
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """卸载插件"""
        pass
    
    def initialize_plugin(self, plugin: TextProcessorPlugin):
        """初始化插件"""
        pass
    
    def cleanup_plugin(self, plugin: TextProcessorPlugin):
        """清理插件资源"""
        pass
    
    def get_plugin_status(self, plugin_name: str) -> PluginStatus:
        """获取插件状态"""
        pass
```

### 3. 插件配置管理器 (`PluginConfigManager`)

**功能**:
- 插件特定配置管理
- 配置验证和默认值
- 配置热更新
- 配置继承和覆盖

**设计**:
```python
class PluginConfigManager:
    """插件配置管理"""
    
    def get_plugin_config(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件配置"""
        pass
    
    def update_plugin_config(self, plugin_name: str, config: Dict[str, Any]):
        """更新插件配置"""
        pass
    
    def validate_plugin_config(self, plugin_name: str, config: Dict[str, Any]) -> bool:
        """验证插件配置"""
        pass
    
    def get_default_config(self, plugin_name: str) -> Dict[str, Any]:
        """获取插件默认配置"""
        pass
```

### 4. 插件安全沙箱 (`PluginSandbox`)

**功能**:
- 插件权限控制
- 资源访问限制
- 安全执行环境
- 恶意代码防护

**设计**:
```python
class PluginSandbox:
    """插件安全沙箱"""
    
    def create_environment(self, permissions: List[str]) -> SandboxEnvironment:
        """创建沙箱环境"""
        pass
    
    def execute_plugin(self, plugin: TextProcessorPlugin, input_data: Any) -> Any:
        """在沙箱中执行插件"""
        pass
    
    def check_permissions(self, plugin_name: str, resource: str) -> bool:
        """检查插件权限"""
        pass
    
    def log_security_event(self, plugin_name: str, event: str):
        """记录安全事件"""
        pass
```

### 5. 插件事件系统 (`PluginEventSystem`)

**功能**:
- 插件间通信
- 事件发布/订阅
- 异步事件处理
- 事件路由和过滤

**设计**:
```python
class PluginEventSystem:
    """插件事件系统"""
    
    def __init__(self):
        self.listeners = {}
        self.event_queue = Queue()
    
    def register_listener(self, event_type: str, callback: Callable):
        """注册事件监听器"""
        pass
    
    def emit_event(self, event_type: str, data: Any = None):
        """发送事件"""
        pass
    
    def unregister_listener(self, event_type: str, callback: Callable):
        """取消注册事件监听器"""
        pass
    
    def process_events(self):
        """处理事件队列"""
        pass
```

### 6. 插件性能监控 (`PluginPerformanceMonitor`)

**功能**:
- 执行时间统计
- 内存使用监控
- 性能报告生成
- 性能瓶颈分析

**设计**:
```python
class PluginPerformanceMonitor:
    """插件性能监控"""
    
    def __init__(self):
        self.metrics = {}
        self.history = []
    
    def start_monitoring(self, plugin_name: str):
        """开始监控插件"""
        pass
    
    def stop_monitoring(self, plugin_name: str):
        """停止监控插件"""
        pass
    
    def get_performance_metrics(self, plugin_name: str) -> Dict[str, Any]:
        """获取性能指标"""
        pass
    
    def generate_performance_report(self) -> str:
        """生成性能报告"""
        pass
```

## 📁 文件系统管理

### 目录结构
```
SubtitleFormatter/
├── src/subtitleformatter/plugins/    # 插件基础设施
│   ├── base/                         # 插件基类和接口
│   └── manager/                      # 插件管理组件
├── plugins/                          # 统一插件目录
│   ├── builtin/                      # 内置插件
│   ├── examples/                     # 示例插件
│   ├── community/                    # 社区插件
│   ├── username/                     # 个人插件
│   ├── experimental/                 # 实验性插件
│   └── deprecated/                   # 废弃插件
├── scripts/                          # 独立脚本 (保持现状)
├── data/                             # 数据目录
├── models/                           # 模型目录
├── temp/                             # 临时文件目录
└── logs/                             # 日志文件目录
```

**详细目录结构**: 请参考 [插件开发指南](plugin_development_guide.md#插件目录结构) 和 [主重构计划](src_refactor_plan.md#插件目录结构设计) 中的完整目录结构说明。

### 目录管理功能
- **自动创建**: 启动时自动创建必要目录
- **权限管理**: 确保目录访问权限正确
- **清理机制**: 定期清理临时文件和过期日志
- **备份策略**: 重要配置和数据的备份

### 命名规范
- **文件系统层**: 使用下划线 (`text_cleaning`, `punctuation_adder`)
- **命令行层**: 使用连字符 (`text-to-sentences`, `sentence-splitter`)
- **配置引用**: 使用完整命名空间 (`builtin/text_cleaning`)
- **命名空间**: 灵活的命名空间，支持多种组织方式
  - **按分类**: `builtin`, `examples`, `community`, `experimental`, `deprecated`
  - **按来源**: `username`, `organization`, `github_user`
  - **按功能**: `text_processing`, `audio_processing`, `format_conversion`
  - **按状态**: `stable`, `beta`, `alpha`

## 🔄 基础设施集成

### 插件与基础设施的集成方式

#### 1. 依赖注入
```python
class TextProcessor:
    """插件化文本处理器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logger
        self.debug_output = DebugOutput(config.get("debug", {}))
        self.model_manager = ModelManager()
        self.plugin_registry = PluginRegistry()
        self.plugin_lifecycle = PluginLifecycleManager()
        self.plugin_config = PluginConfigManager()
        self.plugin_sandbox = PluginSandbox()
        self.plugin_events = PluginEventSystem()
        self.performance_monitor = PluginPerformanceMonitor()
```

#### 2. 插件初始化
```python
def _create_plugin(self, name: str, config: Dict[str, Any]) -> Optional[TextProcessorPlugin]:
    """创建插件实例并注入基础设施"""
    plugin_class = self.plugin_map.get(name)
    if plugin_class:
        plugin = plugin_class(config)
        
        # 注入基础设施
        plugin.logger = self.logger
        plugin.debug_output = self.debug_output
        plugin.model_manager = self.model_manager
        plugin.config_manager = self.plugin_config
        plugin.event_system = self.plugin_events
        
        return plugin
    return None
```

#### 3. 插件使用基础设施
```python
class MyPlugin(TextProcessorPlugin):
    """示例插件"""
    
    def process(self, input_data: str) -> str:
        # 使用日志系统
        self.logger.info("开始处理文本")
        
        # 使用模型管理器
        if not hasattr(self, 'model'):
            self.model = self.model_manager.get_punctuation_model(self.config)
        
        # 处理逻辑
        result = self.model.restore_punctuation(input_data)
        
        # 使用调试输出
        if self.debug_output:
            stats = {"input_length": len(input_data), "output_length": len(result)}
            self.debug_output.show_step("标点恢复", result, stats)
        
        # 发送事件
        self.event_system.emit_event("plugin_processed", {
            "plugin": self.name,
            "input_length": len(input_data),
            "output_length": len(result)
        })
        
        return result
```

## 📊 基础设施优势

### 1. 开发效率提升
- **统一接口**: 所有插件使用相同的基础设施接口
- **快速开发**: 插件开发者无需关心底层实现
- **标准化**: 一致的开发体验和代码风格

### 2. 系统稳定性
- **错误隔离**: 插件错误不会影响系统稳定性
- **资源管理**: 统一的资源分配和回收
- **安全控制**: 插件权限和访问控制

### 3. 可维护性
- **模块化**: 基础设施组件独立开发和维护
- **版本管理**: 基础设施和插件的独立版本控制
- **升级策略**: 基础设施升级不影响现有插件

### 4. 可扩展性
- **插件生态**: 支持丰富的插件生态系统
- **功能扩展**: 新功能通过插件快速添加
- **平台化**: 从工具升级为平台

## 🎯 总结

SubtitleFormatter 作为插件管理平台，其基础设施组件构成了插件生态系统的基石：

1. **现有基础设施** - 日志、调试、模型、配置、版本、主题等系统
2. **插件平台基础设施** - 注册表、生命周期、配置、沙箱、事件、监控等
3. **文件系统管理** - 统一的目录结构和文件管理
4. **集成机制** - 依赖注入和标准化接口

这些基础设施使得 SubtitleFormatter 从一个简单的文本处理工具，升级为一个真正的**插件化文本处理平台**，为插件开发者提供了完整的开发环境和运行支持。

---

**注意**: 本文档与插件架构设计文档、GUI设计文档和开发指南文档配合使用，形成完整的插件系统文档体系。

# 工作配置与保存配置分离机制

## 概述

本文档描述了配置状态管理的实现细节，解决了配置管理实施过程中遇到的配置管理两难问题。该机制引入了工作配置、保存配置、快照配置三层分离的设计模式，确保配置修改的正确保存和 Restore Last 功能的保护。

## 配置管理两难问题

在实施过程中发现了一个关键的两难问题：

### 问题1：Plugin Chain 中的插件配置修改应该保存到哪里？

- **错误做法**：保存到插件自定义配置文件
- **正确做法**：保存到插件链配置文件

### 问题2：如果直接修改插件链配置文件，会破坏 "Restore Last" 功能

- 因为 Restore Last 需要引用原始的插件链配置文件

## 核心解决方案：工作配置与保存配置分离

### 设计理念

- **工作配置**：当前正在编辑的配置（内存中）
- **保存配置**：持久化的配置（文件中）
- **快照配置**：用于 Restore Last 功能的备份

### 配置状态管理

```python
class ConfigState:
    def __init__(self):
        self.working_config: Dict[str, Any] = {}  # 当前工作配置
        self.saved_config: Dict[str, Any] = {}    # 已保存的配置
        self.snapshot_config: Dict[str, Any] = {} # 用于restore的配置快照
        self.is_dirty: bool = False               # 是否有未保存的修改
```

## 智能保存策略

### 根据插件选择来源决定保存位置

- **点击 Available Plugins 中的插件** → 保存到插件自定义配置文件
- **点击 Plugin Chain 中的插件** → 保存到插件链工作配置

### 配置优先级逻辑

1. **插件链工作配置** (如果来自插件链选择且有修改)
2. **插件链保存配置** (如果来自插件链选择且无修改)
3. **插件自定义配置** (如果来自可用插件列表)
4. **插件默认配置** (兜底)

## Restore Last 功能保护机制

### 快照管理

- **启动时创建快照**：加载配置后立即创建快照
- **快照恢复机制**：Restore Last 时从快照恢复，不影响当前工作
- **自动重新快照**：恢复后重新创建快照

### 实现流程

```
启动 → 加载配置 → 创建快照 → 用户编辑 → 工作配置更新
  ↓
Restore Last → 从快照恢复 → 重新创建快照 → 继续编辑
```

## 自动保存机制

### 实时保存

- 参数修改时立即保存到正确位置
- 根据 `is_from_chain` 参数决定保存目标

### 退出时保存

- 程序退出时自动保存未保存的工作配置
- 状态跟踪：`has_unsaved_changes()` 检查未保存变更

## 技术实现要点

### 新增核心方法

- `update_plugin_config_in_working()` - 更新插件链工作配置
- `get_plugin_config_from_working()` - 获取插件链工作配置
- `save_working_chain_config()` - 保存工作配置
- `create_snapshot()` / `restore_from_snapshot()` - 快照管理

### 信号分离

- `pluginSelected` - 来自可用插件列表的选择
- `pluginChainSelected` - 来自插件链的选择

### 配置协调器增强

- `save_plugin_config_to_chain()` - 保存到插件链工作配置
- `has_unsaved_chain_changes()` - 检查未保存变更
- `create_chain_snapshot()` / `restore_chain_from_snapshot()` - 快照管理

## 解决的问题

✅ **插件链配置修改保存位置正确**：现在会保存到插件链配置文件

✅ **Restore Last 功能不受影响**：通过快照机制保护原始配置

✅ **配置修改不丢失**：工作配置确保修改实时保存

✅ **配置优先级正确**：按照设计文档的要求实现优先级

## 用户体验改进

- **无缝编辑**：修改插件链中的插件配置后，切换再回来不会丢失
- **智能保存**：根据选择来源自动保存到正确位置
- **安全恢复**：Restore Last 功能完全不受影响
- **状态可见**：通过日志可以清楚看到配置的保存和加载过程

## 相关文档

- [配置管理设计方案](configuration_management_design.md) - 主要设计文档
- [插件开发指南](plugin_development_guide.md) - 插件开发详情
- [插件架构设计](plugin_architecture_design.md) - 插件架构概述
# ModelManager 迁移计划

## 📋 概述

将现有的 `ModelManager` 从 spaCy 模型管理迁移到 `deepmultilingualpunctuation` 模型管理，同时继承现有的优秀模型管理方式。

**文档定位**: 本文档专注于**ModelManager迁移**，是主重构计划的后续任务。整体实施计划请参考 [主重构计划](src_refactor_plan.md)，基础设施架构请参考 [基础设施架构文档](infrastructure_architecture.md)。

## 🔍 现状分析

### 现有 ModelManager 优势
- ✅ 统一的 `/models/` 目录管理
- ✅ 本地模型缓存机制
- ✅ 自动下载和复制逻辑
- ✅ 完善的错误处理和日志记录
- ✅ 支持离线使用

### 迁移目标
- 🔄 从 spaCy 模型切换到 `deepmultilingualpunctuation` 模型
- 📁 支持 Hugging Face 模型下载和管理
- 🔌 保持离线使用能力
- 🎯 统一接口设计

## 🎯 重构目标

### 新的 ModelManager 设计
```python
class ModelManager:
    """语言模型管理器 - 支持 deepmultilingualpunctuation"""
    
    @staticmethod
    def get_punctuation_model(config):
        """获取标点恢复模型实例
        
        Args:
            config: 配置字典，包含：
                   - model_name: 模型名称 (默认: 'oliverguhr/fullstop-punctuation-multilang-large')
                   - local_models_dir: 本地模型目录 (默认: 'models/')
        
        Returns:
            PunctuationModel: 加载好的标点恢复模型
        """
        # 继承现有的模型管理逻辑
        # 1. 检查本地模型是否存在
        # 2. 如果不存在，从 Hugging Face 下载
        # 3. 支持离线使用
        pass
```

## 📝 详细实施计划

### 阶段一：架构设计 (1天)

#### 1.1 接口设计
- 保持与现有 `ModelManager` 相似的 API
- 支持配置驱动的模型选择
- 统一的错误处理机制

#### 1.2 模型管理策略
- 继承现有的 `/models/` 目录结构
- 支持 Hugging Face 模型下载
- 实现本地模型缓存机制

### 阶段二：实现开发 (2天)

#### 2.1 核心功能实现
- 实现 `get_punctuation_model` 方法
- 实现模型下载和缓存逻辑
- 实现离线使用支持

#### 2.2 错误处理
- 继承现有的完善错误处理机制
- 添加网络连接错误处理
- 添加模型加载失败处理

### 阶段三：测试验证 (1天)

#### 3.1 功能测试
- 测试模型下载功能
- 测试本地模型加载
- 测试离线使用场景

#### 3.2 集成测试
- 与 `punctuation_adder` 组件集成测试
- 性能测试
- 错误场景测试

## 🔧 技术实现要点

### 1. 继承现有架构
- 保持 `/models/` 目录结构和缓存逻辑
- 使用相同的日志记录机制
- 保持相同的配置管理方式

### 2. 支持离线使用
- 参考 `model_storage_summary.md` 的实现方式
- 支持本地模型路径指定
- 实现模型文件完整性检查

### 3. 统一接口
- 保持与现有 `ModelManager` 相似的 API
- 支持配置驱动的模型选择
- 提供向后兼容的接口

## 📚 参考文档

- `docs/plan/ref/model_storage_summary.md` - 模型存储方案
- `docs/plan/ref/process_texts.py` - 本地模型使用示例
- `src/subtitleformatter/models/model_manager.py` - 现有实现

## ⚠️ 注意事项

### 依赖管理
- 需要添加 `deepmultilingualpunctuation` 依赖
- 可能需要添加 `transformers` 和 `torch` 依赖
- 考虑模型文件大小对项目的影响

### 性能考虑
- 模型加载时间可能较长
- 内存使用量可能增加
- 需要考虑模型缓存策略

## 🚀 实施时间表

| 阶段 | 任务 | 预计时间 | 优先级 |
|------|------|----------|--------|
| 1 | 架构设计 | 1天 | 中 |
| 2 | 实现开发 | 2天 | 中 |
| 3 | 测试验证 | 1天 | 中 |
| **总计** | | **4天** | **靠后** |

## 📋 验收标准

### 功能验收
- [ ] 模型下载功能正常
- [ ] 本地模型加载正常
- [ ] 离线使用功能正常
- [ ] 与 `punctuation_adder` 集成正常

### 性能验收
- [ ] 模型加载时间合理
- [ ] 内存使用量可控
- [ ] 缓存机制有效

### 质量验收
- [ ] 错误处理完善
- [ ] 日志记录完整
- [ ] 代码质量良好

---

**注意**: 此计划为独立事项，优先级靠后，在主要重构完成后进行。

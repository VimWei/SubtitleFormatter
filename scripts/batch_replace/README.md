# 批量搜索替换工具 (Vim脚本)

## 功能描述
通用Vim批量搜索替换脚本，支持多模式字典、递归搜索、错误抑制、操作日志。

## 使用方法

### 通过Vim执行
```bash
# 在Vim中打开目标目录，然后执行脚本
:source scripts/batch_replace/main.vim
```

### 直接运行
```bash
vim -S scripts/batch_replace/main.vim
```

## 配置说明
脚本支持多种配置方案：

### 文件搜索范围
- 所有文件: `**/*`
- 特定类型: `**/*.txt **/*.md **/*.py`
- 当前目录: `*`
- 特定目录: `src/**/*`

### 替换规则
在脚本中修改 `g:replacement_dict` 字典：
```vim
let g:replacement_dict = {
    \ '旧词': '新词',
    \ '模式': '替换内容',
    \ }
```

### 搜索选项
- `g:case_sensitive`: 是否区分大小写
- `g:use_regex`: 是否使用正则表达式
- `g:confirm_each`: 是否每次替换前确认
- `g:backup_files`: 是否创建备份文件

## 输出
- 操作日志显示在Vim窗口中
- 统计信息包括替换次数、修改文件数等

## 示例
```bash
# 批量替换项目中的词汇
vim -S scripts/batch_replace/main.vim
```

# 文本重分段工具 (Vim脚本)

## 功能描述
使用Vim脚本对文本进行智能重分段，处理停顿词、标点符号和连接词。

## 使用方法

### 通过Vim执行
```bash
# 在Vim中打开文本文件，然后执行脚本
:source scripts/txt_resegment/main.vim
```

### 直接运行
```bash
vim -S scripts/txt_resegment/main.vim <input_file>
```

## 处理规则
- 移除停顿词 (um, uh等)
- 处理标点符号断句 (. ! ?)
- 处理连接词断行 (and, because, so, then, but等)
- 清理多余空格
- 删除空行

## 输出
- 处理后的文本直接保存到原文件

## 示例
```bash
# 使用Vim处理文本文件
vim -S scripts/txt_resegment/main.vim input.txt
```

#!/usr/bin/env python3
"""
Punctuation Adder - 自动标点恢复工具

使用机器学习模型为英文文本自动添加标点符号，提升文本可读性。
支持单文件和通配符批量处理。
"""

import argparse
import glob
import os
import re
import sys
from pathlib import Path

try:
    from deepmultilingualpunctuation import PunctuationModel
except ImportError:
    print("错误: 缺少依赖包 'deepmultilingualpunctuation'")
    print("请运行: uv sync --group punctuation-adder")
    sys.exit(1)


def resolve_input_path(filename):
    """解析输入文件路径，支持默认路径处理"""
    if os.path.exists(filename):
        return filename  # 完整路径或当前目录文件

    # 尝试在默认输入目录中查找
    default_path = os.path.join("data", "input", filename)
    if os.path.exists(default_path):
        return default_path

    # 创建默认目录并返回路径
    os.makedirs("data/input", exist_ok=True)
    return default_path


def resolve_output_path(input_path, output_filename=None):
    """解析输出文件路径，支持默认路径处理"""
    if output_filename:
        return os.path.join("data", "output", output_filename)

    # 根据输入文件名生成输出文件名
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    return os.path.join("data", "output", f"{base_name}.punctuated.txt")


def process_text_file(model, input_filepath, output_filepath):
    """
    处理单个文本文件，添加标点符号

    Args:
        model: PunctuationModel 实例
        input_filepath: 输入文件路径
        output_filepath: 输出文件路径

    Returns:
        bool: 处理是否成功
    """
    filename = os.path.basename(input_filepath)

    try:
        # 使用 utf-8-sig 处理可能的 BOM (字节顺序标记)
        with open(input_filepath, "r", encoding="utf-8-sig") as f:
            text = f.read()

        if not text.strip():
            print(f"跳过空文件: '{filename}'")
            with open(output_filepath, "w", encoding="utf-8") as f:
                f.write("")  # 创建空输出文件
            return True

        # 步骤1: 使用简单且强大的 restore_punctuation 方法
        # 它自动处理长文本
        punctuated_text = model.restore_punctuation(text)

        # 步骤2: 分割文本为句子
        # 正则表达式在句号、问号或感叹号后分割文本
        sentences = re.split(r"(?<=[.?!])\s+", punctuated_text.strip())

        # 步骤3: 为每个句子首字母大写并换行
        processed_lines = []
        for sentence in sentences:
            s = sentence.strip()
            if s:
                # 找到第一个字母并大写，保留其余字母的大小写
                for i, char in enumerate(s):
                    if char.isalpha():
                        processed_lines.append(s[:i] + s[i].upper() + s[i + 1 :])
                        break
                else:
                    processed_lines.append(s)  # 如果没找到字母则直接添加

        capitalized_text = "\n".join(processed_lines)

        # 步骤4: 应用用户精确的替换规则
        result = capitalized_text.replace(" - ", ", ")
        result = result.replace("- ", ", ")

        # 步骤5: 将最终修正的文本写入输出文件
        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write(result)

        print(f"成功保存标点文本到 '{output_filepath}'")
        return True

    except Exception as e:
        print(f"处理文件 {filename} 失败: {e}")
        return False


def expand_file_pattern(pattern):
    """展开文件模式，支持通配符"""
    if "*" in pattern or "?" in pattern:
        # 处理通配符模式
        expanded_files = glob.glob(pattern)
        if not expanded_files:
            # 尝试在默认目录中查找
            default_pattern = os.path.join("data", "input", pattern)
            expanded_files = glob.glob(default_pattern)
        return expanded_files
    else:
        # 单个文件
        return [pattern]


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="自动标点恢复工具 - 使用机器学习模型为英文文本添加标点符号",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  %(prog)s file.txt                    # 处理单个文件
  %(prog)s *.txt                       # 处理当前目录所有 .txt 文件
  %(prog)s data/input/*.txt            # 处理指定目录的 .txt 文件
  %(prog)s file.txt -o output.txt      # 指定输出文件名
  %(prog)s --help                      # 显示此帮助信息

默认路径处理:
  - 输入文件: 优先查找 data/input/ 目录
  - 输出文件: 自动保存到 data/output/ 目录
  - 目录不存在时自动创建
        """,
    )

    parser.add_argument("input", help="输入文件或文件模式（支持通配符 *.txt）")

    parser.add_argument("-o", "--output", help="输出文件（可选，默认自动生成）")

    parser.add_argument("--version", action="version", version="Punctuation Adder v1.0.0")

    args = parser.parse_args()

    # 展开文件模式
    input_files = expand_file_pattern(args.input)

    if not input_files:
        print(f"错误: 未找到匹配的文件: {args.input}")
        print("提示: 支持通配符模式，如 *.txt")
        return 1

    print(f"找到 {len(input_files)} 个文件待处理")

    # 初始化模型
    print("正在加载标点模型... (这可能需要一些时间)")
    try:
        model = PunctuationModel()
        print("模型加载完成")
    except Exception as e:
        print(f"模型加载失败: {e}")
        return 1

    # 处理每个文件
    success_count = 0
    for input_filepath in input_files:
        # 解析路径
        resolved_input = resolve_input_path(input_filepath)
        resolved_output = resolve_output_path(resolved_input, args.output)

        # 确保输出目录存在
        os.makedirs(os.path.dirname(resolved_output), exist_ok=True)

        filename = os.path.basename(resolved_input)
        print(f"正在处理 '{filename}'...")

        if process_text_file(model, resolved_input, resolved_output):
            success_count += 1

    print(f"\n处理完成: {success_count}/{len(input_files)} 个文件成功处理")

    if success_count == len(input_files):
        return 0
    else:
        print(f"警告: {len(input_files) - success_count} 个文件处理失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

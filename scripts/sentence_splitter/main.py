#!/usr/bin/env python3
"""
句子分割工具 - 将文本按句分割，每句一行
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, TextIO


class SentenceSplitter:
    """句子分割器"""

    def __init__(self):
        pass

    def split_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子列表

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        if not text.strip():
            return []

        # 预处理：统一换行符，将换行符替换为空格
        text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")

        # 使用正则表达式分割句子
        # 匹配句号、问号、感叹号后跟空格或文本结束
        sentence_pattern = re.compile(r"([.!?]+)\s+")

        # 分割句子
        parts = sentence_pattern.split(text)

        sentences = []
        current_sentence = ""

        for i, part in enumerate(parts):
            if i % 2 == 0:  # 偶数索引是句子内容
                current_sentence += part
            else:  # 奇数索引是标点符号
                current_sentence += part
                # 检查句子是否完整
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""

        # 添加最后一个句子（如果有）
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        return sentences

    def _is_abbreviation(self, text: str, pos: int) -> bool:
        """
        检查位置pos的句号是否是缩写的一部分

        Args:
            text: 文本
            pos: 句号位置

        Returns:
            是否是缩写
        """
        # 检查前面的字符
        if pos < 2:
            return False

        # 检查是否是单字母缩写（如 "U.S."）
        if pos >= 2 and text[pos - 1].isupper() and text[pos - 2] == " ":
            return True

        # 检查是否是常见缩写
        abbrev_patterns = ["Mr.", "Mrs.", "Dr.", "Prof.", "Inc.", "Ltd.", "Co.", "Corp."]
        for pattern in abbrev_patterns:
            if text[pos - len(pattern) + 1 : pos + 1] == pattern:
                return True

        return False

    def process_file(self, input_file: Path, output_file: Path = None) -> None:
        """
        处理文件，将文本按句分割

        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径，如果为None则自动生成输出文件路径
        """
        try:
            # 读取输入文件
            with open(input_file, "r", encoding="utf-8") as f:
                text = f.read()

            # 分割句子
            sentences = self.split_sentences(text)

            # 如果没有指定输出文件，自动生成输出文件路径
            if output_file is None:
                # 获取输入文件名（不含扩展名）
                input_stem = input_file.stem
                # 生成输出文件路径：data/output/原文件名.txt
                output_file = Path("data/output") / f"{input_stem}.txt"
                # 确保输出目录存在
                output_file.parent.mkdir(parents=True, exist_ok=True)

            # 写入输出文件
            with open(output_file, "w", encoding="utf-8") as f:
                for sentence in sentences:
                    f.write(sentence + "\n")
            print(f"已处理 {len(sentences)} 个句子，保存到: {output_file}")

        except FileNotFoundError:
            print(f"❌ 错误：找不到输入文件 {input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="句子分割工具 - 将文本按句分割，每句一行",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py input.txt                    # 输出到控制台
  python main.py input.txt -o output.txt      # 输出到文件
  python main.py input.txt --output output.txt # 输出到文件
        """,
    )

    parser.add_argument("input_file", help="输入文本文件路径")

    parser.add_argument(
        "-o", "--output", dest="output_file", help="输出文件路径（可选，不指定则输出到控制台）"
    )

    parser.add_argument("--version", action="version", version="句子分割工具 v1.0.0")

    args = parser.parse_args()

    # 验证输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在: {input_path}")
        sys.exit(1)

    if not input_path.is_file():
        print(f"❌ 错误：输入路径不是文件: {input_path}")
        sys.exit(1)

    # 处理输出文件路径
    output_path = None
    if args.output_file:
        output_path = Path(args.output_file)
        # 确保输出目录存在
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建分割器并处理文件
    splitter = SentenceSplitter()
    splitter.process_file(input_path, output_path)


if __name__ == "__main__":
    main()

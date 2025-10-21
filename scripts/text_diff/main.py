#!/usr/bin/env python3
"""
文本差异检测工具
比较两个文本文件，识别除了格式化差异之外的词汇差异
"""

import os
import sys
import time
from dataclasses import dataclass
from typing import Optional

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from diff_reporter import DiffReporter
from sequence_aligner import SequenceAligner
from text_normalizer import TextNormalizer
from utils import (
    format_duration,
    format_file_size,
    get_file_info,
    print_error,
    print_info,
    print_separator,
    print_success,
    print_warning,
    read_file_safely,
    validate_file_path,
)


@dataclass
class DiffConfig:
    """差异检测配置"""

    ignore_case: bool = True
    ignore_punctuation: bool = True
    ignore_whitespace: bool = True
    min_word_length: int = 1
    show_context: int = 3
    color_output: bool = True
    console_output: bool = True


@dataclass
class OutputConfig:
    """输出配置"""

    console_output: bool = True
    json_output: bool = False
    html_output: bool = False
    csv_output: bool = False
    output_dir: str = "data/output"
    output_prefix: str = "diff_result"


class TextDiffer:
    """文本差异检测器"""

    def __init__(self, config: DiffConfig = None):
        """
        初始化差异检测器

        Args:
            config: 配置对象
        """
        self.config = config or DiffConfig()
        self.normalizer = TextNormalizer()
        self.aligner = SequenceAligner()
        self.reporter = DiffReporter(color_output=self.config.color_output)

    def compare_files(self, old_file: str, new_file: str) -> Optional[object]:
        """
        比较两个文件

        Args:
            old_file: 旧文件路径
            new_file: 新文件路径

        Returns:
            result: 比较结果，如果失败返回None
        """
        start_time = time.time()

        print_separator()
        print_info("开始文件差异检测")
        print_separator()

        # 验证文件
        if not self._validate_files(old_file, new_file):
            return None

        # 读取文件
        old_content, old_error = read_file_safely(old_file)
        new_content, new_error = read_file_safely(new_file)

        if old_error:
            print_error(f"读取旧文件失败: {old_error}")
            return None

        if new_error:
            print_error(f"读取新文件失败: {new_error}")
            return None

        # 显示文件信息
        self._show_file_info(old_file, new_file, old_content, new_content)

        # 标准化文本
        print_info("正在标准化文本...")
        old_normalized, old_stats = self.normalizer.normalize(old_content)
        new_normalized, new_stats = self.normalizer.normalize(new_content)

        # 提取词汇
        print_info("正在提取词汇...")
        old_words = self.normalizer.extract_words(old_normalized)
        new_words = self.normalizer.extract_words(new_normalized)

        # 获取位置信息
        old_positions = self.normalizer.get_word_positions(old_normalized)
        new_positions = self.normalizer.get_word_positions(new_normalized)

        print_info(f"旧文件词汇数: {len(old_words)}")
        print_info(f"新文件词汇数: {len(new_words)}")

        # 进行序列对齐
        print_info("正在进行序列对齐...")
        result = self.aligner.align_sequences(old_words, new_words, old_positions, new_positions)

        # 计算处理时间
        processing_time = time.time() - start_time

        # 显示结果
        self._show_results(result, old_file, new_file, processing_time)

        return result

    def _validate_files(self, old_file: str, new_file: str) -> bool:
        """
        验证文件

        Args:
            old_file: 旧文件路径
            new_file: 新文件路径

        Returns:
            is_valid: 是否有效
        """
        # 验证旧文件
        is_valid, error = validate_file_path(old_file)
        if not is_valid:
            print_error(f"旧文件验证失败: {error}")
            return False

        # 验证新文件
        is_valid, error = validate_file_path(new_file)
        if not is_valid:
            print_error(f"新文件验证失败: {error}")
            return False

        return True

    def _show_file_info(self, old_file: str, new_file: str, old_content: str, new_content: str):
        """
        显示文件信息

        Args:
            old_file: 旧文件路径
            new_file: 新文件路径
            old_content: 旧文件内容
            new_content: 新文件内容
        """
        old_info = get_file_info(old_file)
        new_info = get_file_info(new_file)

        print_info("文件信息:")
        print(f"  旧文件: {old_info['name']} ({format_file_size(old_info['size'])})")
        print(f"  新文件: {new_info['name']} ({format_file_size(new_info['size'])})")
        print(f"  旧文件字符数: {len(old_content):,}")
        print(f"  新文件字符数: {len(new_content):,}")

    def _show_results(self, result: object, old_file: str, new_file: str, processing_time: float):
        """
        显示结果

        Args:
            result: 比较结果
            old_file: 旧文件路径
            new_file: 新文件路径
            processing_time: 处理时间
        """
        print_separator()
        print_success(f"差异检测完成 (耗时: {format_duration(processing_time)})")
        print_separator()

        # 显示详细报告
        if self.config.console_output:
            self.reporter.print_console_report(result, old_file, new_file, self.config.show_context)

    def save_reports(
        self, result: object, output_config: OutputConfig, old_file: str, new_file: str
    ):
        """
        保存报告

        Args:
            result: 比较结果
            output_config: 输出配置
            old_file: 旧文件路径
            new_file: 新文件路径
        """
        if not any(
            [output_config.json_output, output_config.html_output, output_config.csv_output]
        ):
            return

        print_info("正在保存报告...")

        # 确保输出目录存在
        from utils import ensure_directory

        ensure_directory(output_config.output_dir)

        # 生成基础文件名
        base_name = f"{output_config.output_prefix}_{int(time.time())}"

        # 保存JSON报告
        if output_config.json_output:
            json_file = os.path.join(output_config.output_dir, f"{base_name}.json")
            self.reporter.save_json_report(result, json_file)

        # 保存HTML报告
        if output_config.html_output:
            html_file = os.path.join(output_config.output_dir, f"{base_name}.html")
            self.reporter.save_html_report(result, html_file, old_file, new_file)

        # 保存CSV报告
        if output_config.csv_output:
            csv_file = os.path.join(output_config.output_dir, f"{base_name}.csv")
            self.reporter.save_csv_report(result, csv_file)


def main():
    """主函数"""
    if len(sys.argv) < 3:
        print("用法: python text_diff.py <旧文件> <新文件> [选项]")
        print("\n选项:")
        print("  --json              输出JSON格式报告")
        print("  --html              输出HTML格式报告")
        print("  --csv               输出CSV格式报告")
        print("  --output-dir DIR    输出目录 (默认: 当前目录)")
        print("  --no-color          禁用彩色输出")
        print("  --context N         显示上下文行数 (默认: 3)")
        print("  --help              显示帮助信息")
        sys.exit(1)

    old_file = sys.argv[1]
    new_file = sys.argv[2]

    # 解析命令行参数
    output_config = OutputConfig()
    diff_config = DiffConfig()

    i = 3
    while i < len(sys.argv):
        arg = sys.argv[i]

        if arg == "--json":
            output_config.json_output = True
        elif arg == "--html":
            output_config.html_output = True
        elif arg == "--csv":
            output_config.csv_output = True
        elif arg == "--output-dir" and i + 1 < len(sys.argv):
            output_config.output_dir = sys.argv[i + 1]
            i += 1
        elif arg == "--no-color":
            diff_config.color_output = False
        elif arg == "--context" and i + 1 < len(sys.argv):
            try:
                diff_config.show_context = int(sys.argv[i + 1])
                i += 1
            except ValueError:
                print_error("上下文行数必须是整数")
                sys.exit(1)
        elif arg == "--help":
            print("文本差异检测工具")
            print("比较两个文本文件，识别除了格式化差异之外的词汇差异")
            print("\n用法: python text_diff.py <旧文件> <新文件> [选项]")
            print("\n选项:")
            print("  --json              输出JSON格式报告")
            print("  --html              输出HTML格式报告")
            print("  --csv               输出CSV格式报告")
            print("  --output-dir DIR    输出目录 (默认: 当前目录)")
            print("  --no-color          禁用彩色输出")
            print("  --context N         显示上下文行数 (默认: 3)")
            print("  --help              显示帮助信息")
            sys.exit(0)
        else:
            print_error(f"未知选项: {arg}")
            sys.exit(1)

        i += 1

    # 创建差异检测器
    differ = TextDiffer(diff_config)

    # 执行比较
    result = differ.compare_files(old_file, new_file)

    if result is None:
        print_error("文件比较失败")
        sys.exit(1)

    # 保存报告
    differ.save_reports(result, output_config, old_file, new_file)

    # 根据结果设置退出码
    if result.total_differences > 0:
        sys.exit(2)  # 有差异
    else:
        sys.exit(0)  # 无差异


if __name__ == "__main__":
    main()

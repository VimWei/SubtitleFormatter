#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
字幕格式转换器
将非标准格式的字幕文件转换为标准SRT格式
支持输入文件：.transcript 文件（输出为 .srt 和 .txt）
"""

import re
import sys
from typing import List, Tuple


def parse_timestamp(timestamp: str) -> str:
    """
    将时间戳从 'm:ss' 格式转换为 '00:00:00,000' 格式

    Args:
        timestamp: 输入时间戳，如 '0:02', '1:30'

    Returns:
        标准SRT时间格式，如 '00:00:02,000'
    """
    # 匹配 m:ss 或 mm:ss 格式
    match = re.match(r"(\d+):(\d{2})", timestamp)
    if not match:
        raise ValueError(f"无法解析时间戳格式: {timestamp}")

    minutes = int(match.group(1))
    seconds = int(match.group(2))

    # 转换为标准SRT格式: HH:MM:SS,mmm
    total_seconds = minutes * 60 + seconds
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"


def calculate_end_time(start_time: str, next_start_time: str) -> str:
    """
    计算字幕的结束时间

    Args:
        start_time: 开始时间戳
        next_start_time: 下一个字幕的开始时间戳

    Returns:
        结束时间戳
    """
    # 解析开始时间
    start_match = re.match(r"(\d+):(\d{2})", start_time)
    next_match = re.match(r"(\d+):(\d{2})", next_start_time)

    if not start_match or not next_match:
        # 如果无法解析下一个时间，则假设持续3秒
        start_minutes = int(start_match.group(1)) if start_match else 0
        start_seconds = int(start_match.group(2)) if start_match else 0
        total_seconds = start_minutes * 60 + start_seconds + 3
    else:
        start_minutes = int(start_match.group(1))
        start_seconds = int(start_match.group(2))
        next_minutes = int(next_match.group(1))
        next_seconds = int(next_match.group(2))

        start_total = start_minutes * 60 + start_seconds
        next_total = next_minutes * 60 + next_seconds
        total_seconds = next_total

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"


def parse_subtitle_file(filename: str) -> List[Tuple[str, str, str]]:
    """
    解析非标准格式的字幕文件

    Args:
        filename: 输入文件名

    Returns:
        字幕列表，每个元素包含 (开始时间, 结束时间, 文本)
    """
    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    subtitles = []
    i = 0

    while i < len(lines):
        # 查找时间戳行
        if re.match(r"\d+:\d{2}", lines[i]):
            timestamp = lines[i]
            text_lines = []

            # 收集后续的文本行，直到遇到下一个时间戳或文件结束
            i += 1
            while i < len(lines) and not re.match(r"\d+:\d{2}", lines[i]):
                text_lines.append(lines[i])
                i += 1

            if text_lines:
                # 合并文本行
                text = " ".join(text_lines)

                # 计算结束时间
                if i < len(lines) and re.match(r"\d+:\d{2}", lines[i]):
                    next_timestamp = lines[i]
                    end_time = calculate_end_time(timestamp, next_timestamp)
                else:
                    # 最后一个字幕，假设持续3秒
                    end_time = calculate_end_time(timestamp, timestamp)

                start_time = parse_timestamp(timestamp)
                subtitles.append((start_time, end_time, text))
        else:
            i += 1

    return subtitles


def write_srt_file(subtitles: List[Tuple[str, str, str]], output_filename: str):
    """
    将字幕写入标准SRT格式文件

    Args:
        subtitles: 字幕列表
        output_filename: 输出文件名
    """
    with open(output_filename, "w", encoding="utf-8") as f:
        for i, (start_time, end_time, text) in enumerate(subtitles, 1):
            f.write(f"{i}\n")
            f.write(f"{start_time} --> {end_time}\n")
            f.write(f"{text}\n")
            f.write("\n")


def write_txt_file(subtitles: List[Tuple[str, str, str]], output_filename: str):
    """
    将字幕写入纯文本文件，去除时间轴信息，仅保留正文文本

    Args:
        subtitles: 字幕列表
        output_filename: 输出文件名
    """
    with open(output_filename, "w", encoding="utf-8") as f:
        for _, _, text in subtitles:
            if text.strip():  # 只写入非空文本
                f.write(f"{text.strip()}\n")


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python Transcript_converter.py <输入文件>")
        print("示例: python Transcript_converter.py 'input.transcript'")
        sys.exit(1)

    input_file = sys.argv[1]

    # 根据输入文件扩展名确定输出文件名
    if input_file.endswith(".transcript"):
        base_name = input_file.replace(".transcript", "")
        srt_output_file = base_name + ".srt"
        txt_output_file = base_name + ".txt"
    else:
        # 如果没有扩展名，添加 .srt 和 .txt 扩展名
        srt_output_file = input_file + ".srt"
        txt_output_file = input_file + ".txt"

    try:
        print(f"正在解析文件: {input_file}")
        subtitles = parse_subtitle_file(input_file)

        print(f"找到 {len(subtitles)} 条字幕")

        print(f"正在写入标准SRT文件: {srt_output_file}")
        write_srt_file(subtitles, srt_output_file)

        print(f"正在写入纯文本文件: {txt_output_file}")
        write_txt_file(subtitles, txt_output_file)

        print("转换完成！")
        print(f"输出文件: {srt_output_file}")
        print(f"输出文件: {txt_output_file}")

    except FileNotFoundError:
        print(f"错误: 找不到文件 '{input_file}'")
        sys.exit(1)
    except Exception as e:
        print(f"错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

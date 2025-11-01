"""
TranscriptConverterPlugin - 字幕格式转换插件

这个插件将非标准格式的字幕文件转换为标准SRT格式，支持：
- 将 .transcript 文件转换为 .srt 文件
- 将 .transcript 文件转换为 .txt 文件（纯文本）

注意：该插件在输出目录模式下工作，接收文件路径作为输入，
在指定的输出目录中生成多个文件。
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple

from subtitleformatter.plugins.base import TextProcessorPlugin


class TranscriptConverterPlugin(TextProcessorPlugin):
    """
    字幕格式转换插件

    将非标准格式的字幕文件（.transcript）转换为标准SRT格式
    支持输出 .srt 和 .txt 文件
    """

    # 插件元数据
    name = "builtin/transcript_converter"
    version = "1.0.0"
    description = "将 .transcript 转换为 .srt/.txt"
    author = "SubtitleFormatter Team"
    dependencies = []

    # 配置模式
    config_schema = {
        "required": [],
        "optional": {
            "enabled": bool,
            "emit_srt": bool,
            "emit_txt": bool,
        },
        "field_types": {
            "enabled": bool,
            "emit_srt": bool,
            "emit_txt": bool,
        },
    }

    def __init__(self, config: Dict[str, Any] = None):
        """初始化字幕格式转换插件"""
        super().__init__(config)

        # 应用默认配置（基类已从 plugin.json 加载默认值）
        self.enabled = self.config.get("enabled", True)
        self.emit_srt = self.config.get("emit_srt", True)
        self.emit_txt = self.config.get("emit_txt", True)

    def _parse_timestamp(self, timestamp: str) -> str:
        """
        将时间戳从 'm:ss' 格式转换为 '00:00:00,000' 格式

        Args:
            timestamp: 输入时间戳，如 '0:02', '1:30'

        Returns:
            标准SRT时间格式，如 '00:00:02,000'
        """
        match = re.match(r"(\d+):(\d{2})", timestamp)
        if not match:
            raise ValueError(f"无法解析时间戳格式: {timestamp}")
        minutes = int(match.group(1))
        seconds = int(match.group(2))
        total_seconds = minutes * 60 + seconds
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"

    def _calculate_end_time(self, start_time: str, next_start_time: str) -> str:
        """
        计算字幕的结束时间

        Args:
            start_time: 开始时间戳
            next_start_time: 下一个字幕的开始时间戳

        Returns:
            结束时间戳
        """
        next_match = re.match(r"(\d+):(\d{2})", next_start_time)
        if next_match:
            # 如果下一个时间戳存在且有效，使用它作为结束时间
            next_minutes = int(next_match.group(1))
            next_seconds = int(next_match.group(2))
            total_seconds = next_minutes * 60 + next_seconds
        else:
            # 如果没有下一个时间戳，使用开始时间+3秒作为结束时间
            start_match = re.match(r"(\d+):(\d{2})", start_time)
            if start_match:
                start_minutes = int(start_match.group(1))
                start_seconds = int(start_match.group(2))
                total_seconds = start_minutes * 60 + start_seconds + 3
            else:
                # 如果开始时间也无法解析，返回0:00:03,000
                total_seconds = 3

        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},000"

    def _parse_subtitle_file(self, filename: str) -> List[Tuple[str, str, str]]:
        """
        解析非标准格式的字幕文件

        Args:
            filename: 输入文件名

        Returns:
            字幕列表，每个元素包含 (开始时间, 结束时间, 文本)
        """
        with open(filename, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        subtitles: List[Tuple[str, str, str]] = []
        i = 0
        while i < len(lines):
            if re.match(r"\d+:\d{2}", lines[i]):
                timestamp = lines[i]
                text_lines: List[str] = []
                i += 1
                while i < len(lines) and not re.match(r"\d+:\d{2}", lines[i]):
                    text_lines.append(lines[i])
                    i += 1
                if text_lines:
                    text = " ".join(text_lines)
                    if i < len(lines) and re.match(r"\d+:\d{2}", lines[i]):
                        next_timestamp = lines[i]
                        end_time = self._calculate_end_time(timestamp, next_timestamp)
                    else:
                        end_time = self._calculate_end_time(timestamp, timestamp)
                    start_time = self._parse_timestamp(timestamp)
                    subtitles.append((start_time, end_time, text))
            else:
                i += 1
        return subtitles

    def _write_srt_file(self, subtitles: List[Tuple[str, str, str]], output_filename: str) -> None:
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

    def _write_txt_file(self, subtitles: List[Tuple[str, str, str]], output_filename: str) -> None:
        """
        将字幕写入纯文本文件，去除时间轴信息，仅保留正文文本

        Args:
            subtitles: 字幕列表
            output_filename: 输出文件名
        """
        with open(output_filename, "w", encoding="utf-8") as f:
            for _, _, text in subtitles:
                if text.strip():
                    f.write(f"{text.strip()}\n")

    def get_input_type(self) -> type:
        """返回期望的输入数据类型"""
        return str

    def get_output_type(self) -> type:
        """返回输出的数据类型"""
        return list

    def process(self, input_data: str) -> list:
        """
        处理 .transcript 文件，生成 .srt 和 .txt 文件。

        Args:
            input_data: 输入文件路径（字符串）

        Returns:
            生成的文件路径列表

        注意：
            - 输出目录从 self.config["_output_dir"] 获取（由执行层注入）
            - 插件只返回基础文件名（不含时间戳），时间戳由平台层统一处理
            - 插件配置（emit_srt, emit_txt）决定输出哪些格式
        """
        if not self.enabled:
            return []

        input_path = Path(input_data)

        # 输出目录由执行层注入到 config 中
        output_dir_str = self.config.get("_output_dir")
        if output_dir_str:
            output_dir = Path(output_dir_str)
        else:
            # 回退到输入文件所在目录
            output_dir = input_path.parent
        output_dir.mkdir(parents=True, exist_ok=True)

        # 构建基础文件名（不处理时间戳，由平台层统一处理）
        base_name = os.path.splitext(os.path.basename(str(input_path)))[0]

        # 解析输入文件
        subtitles = self._parse_subtitle_file(str(input_path))
        artifacts: list[str] = []

        # 根据插件配置决定输出哪些格式（使用基础文件名，不含时间戳）
        if self.emit_srt:
            srt_output = output_dir / f"{base_name}.srt"
            self._write_srt_file(subtitles, str(srt_output))
            artifacts.append(str(srt_output))

        if self.emit_txt:
            txt_output = output_dir / f"{base_name}.txt"
            self._write_txt_file(subtitles, str(txt_output))
            artifacts.append(str(txt_output))

        return artifacts

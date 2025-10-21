"""
工具函数模块
提供通用的工具函数
"""

import os
import sys
from typing import Optional, Tuple


def read_file_safely(filepath: str) -> Tuple[Optional[str], Optional[str]]:
    """
    安全地读取文件

    Args:
        filepath: 文件路径

    Returns:
        content: 文件内容，如果读取失败返回None
        error: 错误信息，如果没有错误返回None
    """
    try:
        # 检查文件是否存在
        if not os.path.exists(filepath):
            return None, f"文件不存在: {filepath}"

        # 检查文件是否可读
        if not os.access(filepath, os.R_OK):
            return None, f"文件不可读: {filepath}"

        # 尝试不同的编码读取文件
        encodings = ["utf-8", "gbk", "gb2312", "latin-1"]

        for encoding in encodings:
            try:
                with open(filepath, "r", encoding=encoding) as f:
                    content = f.read()
                return content, None
            except UnicodeDecodeError:
                continue

        return None, f"无法解码文件: {filepath}"

    except Exception as e:
        return None, f"读取文件时发生错误: {str(e)}"


def validate_file_path(filepath: str) -> Tuple[bool, Optional[str]]:
    """
    验证文件路径

    Args:
        filepath: 文件路径

    Returns:
        is_valid: 是否有效
        error: 错误信息
    """
    if not filepath:
        return False, "文件路径不能为空"

    if not os.path.exists(filepath):
        return False, f"文件不存在: {filepath}"

    if not os.path.isfile(filepath):
        return False, f"路径不是文件: {filepath}"

    return True, None


def get_file_info(filepath: str) -> dict:
    """
    获取文件信息

    Args:
        filepath: 文件路径

    Returns:
        info: 文件信息字典
    """
    try:
        stat = os.stat(filepath)
        return {
            "path": filepath,
            "name": os.path.basename(filepath),
            "size": stat.st_size,
            "modified": stat.st_mtime,
            "exists": True,
        }
    except Exception:
        return {
            "path": filepath,
            "name": os.path.basename(filepath),
            "size": 0,
            "modified": 0,
            "exists": False,
        }


def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小

    Args:
        size_bytes: 字节数

    Returns:
        formatted_size: 格式化后的大小字符串
    """
    if size_bytes == 0:
        return "0 B"

    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)

    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1

    return f"{size:.1f} {size_names[i]}"


def format_duration(seconds: float) -> str:
    """
    格式化时间长度

    Args:
        seconds: 秒数

    Returns:
        formatted_duration: 格式化后的时间字符串
    """
    if seconds < 1:
        return f"{seconds*1000:.0f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        secs = seconds % 60
        return f"{minutes}m {secs:.1f}s"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        return f"{hours}h {minutes}m {secs:.1f}s"


def ensure_directory(directory: str) -> bool:
    """
    确保目录存在

    Args:
        directory: 目录路径

    Returns:
        success: 是否成功
    """
    try:
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        return True
    except Exception:
        return False


def get_output_filename(base_name: str, extension: str, output_dir: str = ".") -> str:
    """
    生成输出文件名

    Args:
        base_name: 基础文件名
        extension: 文件扩展名
        output_dir: 输出目录

    Returns:
        output_path: 输出文件路径
    """
    # 确保输出目录存在
    ensure_directory(output_dir)

    # 生成文件名
    filename = f"{base_name}.{extension}"
    output_path = os.path.join(output_dir, filename)

    # 如果文件已存在，添加序号
    counter = 1
    while os.path.exists(output_path):
        filename = f"{base_name}_{counter}.{extension}"
        output_path = os.path.join(output_dir, filename)
        counter += 1

    return output_path


def print_progress(current: int, total: int, prefix: str = "进度"):
    """
    打印进度信息

    Args:
        current: 当前进度
        total: 总数
        prefix: 前缀文本
    """
    if total == 0:
        return

    percentage = (current / total) * 100
    bar_length = 30
    filled_length = int(bar_length * current // total)

    bar = "█" * filled_length + "-" * (bar_length - filled_length)

    print(f"\r{prefix}: |{bar}| {percentage:.1f}% ({current}/{total})", end="")

    if current == total:
        print()  # 换行


def print_separator(char: str = "=", length: int = 60):
    """
    打印分隔线

    Args:
        char: 分隔字符
        length: 分隔线长度
    """
    print(char * length)


def print_error(message: str):
    """
    打印错误信息

    Args:
        message: 错误信息
    """
    print(f"错误: {message}", file=sys.stderr)


def print_warning(message: str):
    """
    打印警告信息

    Args:
        message: 警告信息
    """
    print(f"警告: {message}")


def print_info(message: str):
    """
    打印信息

    Args:
        message: 信息
    """
    print(f"信息: {message}")


def print_success(message: str):
    """
    打印成功信息

    Args:
        message: 成功信息
    """
    print(f"成功: {message}")


class ProgressTracker:
    """进度跟踪器"""

    def __init__(self, total: int, prefix: str = "进度"):
        """
        初始化进度跟踪器

        Args:
            total: 总数
            prefix: 前缀文本
        """
        self.total = total
        self.current = 0
        self.prefix = prefix

    def update(self, increment: int = 1):
        """
        更新进度

        Args:
            increment: 增量
        """
        self.current += increment
        print_progress(self.current, self.total, self.prefix)

    def finish(self):
        """完成进度"""
        self.current = self.total
        print_progress(self.current, self.total, self.prefix)

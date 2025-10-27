"""
统一日志系统 - 将终端输出和GUI日志面板连接起来
"""

import sys
from datetime import datetime
from typing import Any, Callable, Optional


class UnifiedLogger:
    """
    统一日志管理器，负责所有终端和GUI输出

    职责：
    - 统一管理终端输出和GUI日志面板
    - 支持简洁模式和详细模式
    - 提供类似print的简单使用方式
    - 自动添加时间戳和日志级别
    - 支持日志级别过滤

    注意：DebugOutput类现在只负责文件保存，不处理终端输出
    """

    # 日志级别优先级
    LOG_LEVELS = {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 2,
        "ERROR": 3,
    }

    def __init__(self):
        self.gui_log_callback: Optional[Callable[[str], None]] = None
        self.terminal_enabled = True
        self.gui_enabled = True
        self.debug_mode = False  # 控制详细日志输出
        self.log_level = "INFO"  # 默认日志级别

    def set_gui_callback(self, callback: Callable[[str], None]) -> None:
        """设置GUI日志回调函数"""
        self.gui_log_callback = callback

    def enable_terminal(self, enabled: bool = True) -> None:
        """启用/禁用终端输出"""
        self.terminal_enabled = enabled

    def enable_gui(self, enabled: bool = True) -> None:
        """启用/禁用GUI输出"""
        self.gui_enabled = enabled

    def set_debug_mode(self, enabled: bool = True) -> None:
        """设置调试模式，控制详细日志输出"""
        self.debug_mode = enabled

    def set_log_level(self, level: str = "INFO") -> None:
        """
        设置日志级别
        
        Args:
            level: 日志级别 (DEBUG, INFO, WARNING, ERROR)
        """
        if level.upper() in self.LOG_LEVELS:
            self.log_level = level.upper()
        else:
            self.log_level = "INFO"

    def should_log(self, level: str) -> bool:
        """
        判断指定级别的日志是否应该输出
        
        Args:
            level: 日志级别
            
        Returns:
            是否应该输出
        """
        current_level = self.LOG_LEVELS.get(self.log_level, 1)
        msg_level = self.LOG_LEVELS.get(level.upper(), 1)
        return msg_level >= current_level

    def log(self, message: str, level: str = "INFO") -> None:
        """
        统一的日志输出方法

        Args:
            message: 日志消息
            level: 日志级别 (INFO, WARNING, ERROR, DEBUG)
        """
        # 根据日志级别过滤
        if not self.should_log(level):
            return

        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {level}: {message}"

        # 输出到终端
        if self.terminal_enabled:
            print(formatted_message)
            sys.stdout.flush()

        # 输出到GUI
        if self.gui_enabled and self.gui_log_callback:
            try:
                self.gui_log_callback(formatted_message)
            except Exception:
                # 如果GUI回调失败，不影响终端输出
                pass

    def info(self, message: str) -> None:
        """信息级别日志"""
        self.log(message, "INFO")

    def warning(self, message: str) -> None:
        """警告级别日志"""
        self.log(message, "WARNING")

    def error(self, message: str) -> None:
        """错误级别日志"""
        self.log(message, "ERROR")

    def debug(self, message: str) -> None:
        """调试级别日志"""
        self.log(message, "DEBUG")

    def step(self, step_name: str, message: str = "") -> None:
        """处理步骤日志"""
        if message:
            self.info(f"{step_name}: {message}")
        else:
            self.info(f"{step_name}...")

    def stats(self, title: str, stats_dict: dict) -> None:
        """统计信息日志 - 仅在调试模式下显示"""
        if not self.debug_mode:
            return

        self.info(f"{title}:")
        self.info("-" * 40)

        for key, value in stats_dict.items():
            if isinstance(value, dict):
                self.info(f"{key}:")
                for sub_key, sub_value in value.items():
                    self.info(f"  - {sub_key}: {sub_value}")
            else:
                self.info(f"  - {key}: {value}")
        self.info("-" * 40)

    def progress(self, current: int, total: int, message: str = "") -> None:
        """进度日志"""
        percentage = int((current / total) * 100) if total > 0 else 0
        if message:
            self.info(f"进度: {percentage}% ({current}/{total}) - {message}")
        else:
            self.info(f"进度: {percentage}% ({current}/{total})")

    def debug_info(self, message: str) -> None:
        """调试信息 - 仅在调试模式下显示"""
        if self.debug_mode:
            self.info(message)

    def debug_step(self, step_name: str, message: str = "") -> None:
        """调试步骤 - 仅在调试模式下显示"""
        if self.debug_mode:
            self.step(step_name, message)


# 全局日志实例
logger = UnifiedLogger()


def log_info(message: str) -> None:
    """便捷的信息日志函数"""
    logger.info(message)


def log_warning(message: str) -> None:
    """便捷的警告日志函数"""
    logger.warning(message)


def log_error(message: str) -> None:
    """便捷的错误日志函数"""
    logger.error(message)


def log_debug(message: str) -> None:
    """便捷的调试日志函数"""
    logger.debug(message)


def log_step(step_name: str, message: str = "") -> None:
    """便捷的步骤日志函数"""
    logger.step(step_name, message)


def log_stats(title: str, stats_dict: dict) -> None:
    """便捷的统计日志函数"""
    logger.stats(title, stats_dict)


def log_progress(current: int, total: int, message: str = "") -> None:
    """便捷的进度日志函数"""
    logger.progress(current, total, message)


def log_debug_info(message: str) -> None:
    """便捷的调试信息函数"""
    logger.debug_info(message)


def log_debug_step(step_name: str, message: str = "") -> None:
    """便捷的调试步骤函数"""
    logger.debug_step(step_name, message)


def set_log_level(level: str) -> None:
    """设置全局日志级别"""
    logger.set_log_level(level)

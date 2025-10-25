"""
TextCleaningPlugin - 基础文本清理插件

这个插件提供基础的文本清理功能，包括：
- 统一空白字符、换行符
- 规范化标点符号（全角转半角）
- 规范化数字（全角转半角）
- 清理多余空行
- 处理中英文之间的空格
"""

import re
from collections import Counter
from typing import Any, Dict, List, Union

from subtitleformatter.plugins.base import TextProcessorPlugin


class TextCleaningPlugin(TextProcessorPlugin):
    """
    基础文本清理插件

    用于统一空白字符、换行符、标点符号并清理多余空行
    """

    # 插件元数据
    name = "builtin/text_cleaning"
    version = "1.0.0"
    description = "基础文本清理插件，用于统一空白字符、换行符、标点符号并清理多余空行"
    author = "SubtitleFormatter Team"
    dependencies = []

    # 配置模式
    config_schema = {
        "required": [],
        "optional": {
            "enabled": bool,
            "normalize_punctuation": bool,
            "normalize_numbers": bool,
            "normalize_whitespace": bool,
            "clean_empty_lines": bool,
            "add_spaces_around_punctuation": bool,
            "remove_bom": bool,
        },
        "field_types": {
            "enabled": bool,
            "normalize_punctuation": bool,
            "normalize_numbers": bool,
            "normalize_whitespace": bool,
            "clean_empty_lines": bool,
            "add_spaces_around_punctuation": bool,
            "remove_bom": bool,
        },
    }

    def __init__(self, config: Dict[str, Any] = None):
        """初始化文本清理插件"""
        super().__init__(config)

        # 应用默认配置
        self.enabled = self.config.get("enabled", True)
        self.normalize_punctuation = self.config.get("normalize_punctuation", True)
        self.normalize_numbers = self.config.get("normalize_numbers", True)
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.clean_empty_lines = self.config.get("clean_empty_lines", True)
        self.add_spaces_around_punctuation = self.config.get("add_spaces_around_punctuation", True)
        self.remove_bom = self.config.get("remove_bom", True)

        # 定义所有需要处理的空白字符
        self.whitespace_chars = {
            "\u0020",  # 普通空格
            "\u00a0",  # 不间断空格
            "\u2002",  # En Space
            "\u2003",  # Em Space
            "\u3000",  # Ideographic Space (全角空格)
            "\t",  # Tab
            "\r",  # Carriage Return
        }
        self.whitespace_pattern = "[" + "".join(self.whitespace_chars) + "]"

        # 定义标点符号映射关系
        self.punctuation_map = {
            "：": ":",  # 全角冒号转半角
            "；": ";",  # 全角分号转半角
            "，": ",",  # 全角逗号转半角
            "。": ".",  # 句号统一为英文句点
            "！": "!",  # 全角感叹号转半角
            "？": "?",  # 全角问号转半角
            '"': '"',  # 中文引号转英文引号
            '"': '"',  # 中文号转英文引号
            """: "'",   # 中文单引号转英文单引号
            """: "'",  # 中文单引号转英文单引号
            "【": "[",  # 全角方括号转半角
            "】": "]",
            "（": "(",  # 全角圆括号转半角
            "）": ")",
            "《": "<",  # 书名号转尖括号
            "》": ">",
            "〈": "<",  # 其他形式的尖括号统一
            "〉": ">",
            "「": '"',  # 其他形式的引号统一
            "」": '"',
            "『": "'",  # 其他形式的引号统一
            "』": "'",
            "、": ",",  # 顿号转逗号
        }

        # 定义需要规范化的数字映射
        self.number_map = {
            "０": "0",
            "１": "1",
            "２": "2",
            "３": "3",
            "４": "4",
            "５": "5",
            "６": "6",
            "７": "7",
            "８": "8",
            "９": "9",
        }

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        执行基础文本清理

        Args:
            text: 原始文本（字符串或字符串列表）

        Returns:
            清理后的文本（保持输入类型）
        """
        if not self.enabled:
            return text

        # 处理输入类型
        if isinstance(text, list):
            return [self._process_single_text(item) for item in text]
        else:
            return self._process_single_text(text)

    def _process_single_text(self, text: str) -> str:
        """
        处理单个文本

        Args:
            text: 原始文本

        Returns:
            清理后的文本
        """
        if not text or not isinstance(text, str):
            return text

        original_text = text

        # 1. 检测并移除 BOM（如果启用）
        if self.remove_bom and text.startswith("\ufeff"):
            text = text[1:]

        # 2. 统一换行符为 \n
        text = text.replace("\r\n", "\n").replace("\r", "\n")

        # 3. 规范化标点符号
        if self.normalize_punctuation:
            for old, new in self.punctuation_map.items():
                text = text.replace(old, new)

        # 4. 规范化数字（全角转半角）
        if self.normalize_numbers:
            for old, new in self.number_map.items():
                text = text.replace(old, new)

        # 5. 处理省略号
        text = re.sub(r"\.{3,}|。{3,}|…+", "...", text)

        # 6. 处理重复的标点符号
        text = re.sub(r"([!?]){2,}", r"\1", text)  # 处理多余的感叹号和问号
        text = re.sub(r"(\.{3})[.]+", r"\1", text)  # 处理超过三个点的省略号

        # 7. 规范化空白字符
        if self.normalize_whitespace:
            # 将所有特殊空白字符统一转换为普通空格
            text = re.sub(self.whitespace_pattern, " ", text)

            # 处理中英文之间的空格
            text = re.sub(r"([\u4e00-\u9fff])([a-zA-Z])", r"\1 \2", text)  # 中文后面的英文
            text = re.sub(r"([a-zA-Z])([\u4e00-\u9fff])", r"\1 \2", text)  # 英文后面的中文

            # 确保标点符号后面有空格（有助于后续处理）
            if self.add_spaces_around_punctuation:
                text = re.sub(r"([,:;.!?])([\u4e00-\u9fff])", r"\1 \2", text)

            # 处理括号内的空格
            text = re.sub(r"\( +", "(", text)
            text = re.sub(r" +\)", ")", text)

            # 删除行末空白
            text = self._clean_line_endings(text)

            # 合并多个空格为单个空格
            text = self._normalize_spaces(text)

        # 8. 确保句子边界清晰
        text = re.sub(r"([.!?])\s*([A-Z])", r"\1\n\2", text)

        # 9. 清理多余的空行
        if self.clean_empty_lines:
            text = self._clean_empty_lines(text)

        return text

    def _clean_line_endings(self, text: str) -> str:
        """删除行末空白"""
        lines = text.splitlines()
        lines = [line.rstrip() for line in lines]
        return "\n".join(lines)

    def _normalize_spaces(self, text: str) -> str:
        """合并多个空格为单个空格"""
        return re.sub(r" +", " ", text)

    def _clean_empty_lines(self, text: str) -> str:
        """删除多余的空行，保留单个空行"""
        text = re.sub(r"\n\s*\n", "\n\n", text)  # 将多个空行统一为一个空行
        return text.strip()

    def get_stats(self, original_text: str, processed_text: str) -> Dict[str, int]:
        """
        获取清理统计信息

        Args:
            original_text: 原始文本
            processed_text: 处理后的文本

        Returns:
            统计信息字典
        """
        stats = {}

        # 计算各种字符的变化
        original_len = len(original_text)
        processed_len = len(processed_text)
        stats["length_change"] = processed_len - original_len

        # 计算标点符号变化
        original_punct = sum(1 for c in original_text if c in self.punctuation_map)
        processed_punct = sum(1 for c in processed_text if c in self.punctuation_map.values())
        stats["punctuation_normalized"] = original_punct - processed_punct

        # 计算数字变化
        original_numbers = sum(1 for c in original_text if c in self.number_map)
        processed_numbers = sum(1 for c in processed_text if c in self.number_map.values())
        stats["numbers_normalized"] = original_numbers - processed_numbers

        return stats

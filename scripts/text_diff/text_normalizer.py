"""
文本标准化模块
负责将文本统一为可比较的格式
"""

import re
from typing import Tuple


class TextNormalizer:
    """文本标准化器"""

    def __init__(self):
        """初始化标准化器"""
        # 标点符号映射表
        self.punctuation_map = {
            "。": ".",
            "，": ",",
            "；": ";",
            "：": ":",
            "！": "!",
            "？": "?",
            '"': '"',
            '"': '"',
            """: "'", """: "'",
            "（": "(",
            "）": ")",
            "【": "[",
            "】": "]",
            "《": "<",
            "》": ">",
            "、": ",",
            "…": "...",
            "—": "-",
            "–": "-",
            "·": ".",
            "•": ".",
            "※": "*",
            "★": "*",
            "☆": "*",
            "◆": "*",
            "◇": "*",
            "■": "*",
            "□": "*",
            "▲": "*",
            "△": "*",
            "●": "*",
            "○": "*",
            "◎": "*",
            "⊙": "*",
            "⊕": "*",
            "⊗": "*",
            "⊙": "*",
            "⊖": "*",
            "⊘": "*",
            "⊚": "*",
            "⊛": "*",
            "⊜": "*",
            "⊝": "*",
            "⊞": "*",
            "⊟": "*",
            "⊠": "*",
            "⊡": "*",
            "⊢": "*",
            "⊣": "*",
            "⊤": "*",
            "⊥": "*",
            "⊦": "*",
            "⊧": "*",
            "⊨": "*",
            "⊩": "*",
            "⊪": "*",
            "⊫": "*",
            "⊬": "*",
            "⊭": "*",
            "⊮": "*",
            "⊯": "*",
            "⊰": "*",
            "⊱": "*",
            "⊲": "*",
            "⊳": "*",
            "⊴": "*",
            "⊵": "*",
            "⊶": "*",
            "⊷": "*",
            "⊸": "*",
            "⊹": "*",
            "⊺": "*",
            "⊻": "*",
            "⊼": "*",
            "⊽": "*",
            "⊾": "*",
            "⊿": "*",
            "⋀": "*",
            "⋁": "*",
            "⋂": "*",
            "⋃": "*",
            "⋄": "*",
            "⋅": "*",
            "⋆": "*",
            "⋇": "*",
            "⋈": "*",
            "⋉": "*",
            "⋊": "*",
            "⋋": "*",
            "⋌": "*",
            "⋍": "*",
            "⋎": "*",
            "⋏": "*",
            "⋐": "*",
            "⋑": "*",
            "⋒": "*",
            "⋓": "*",
            "⋔": "*",
            "⋕": "*",
            "⋖": "*",
            "⋗": "*",
            "⋘": "*",
            "⋙": "*",
            "⋚": "*",
            "⋛": "*",
            "⋜": "*",
            "⋝": "*",
            "⋞": "*",
            "⋟": "*",
            "⋠": "*",
            "⋡": "*",
            "⋢": "*",
            "⋣": "*",
            "⋤": "*",
            "⋥": "*",
            "⋦": "*",
            "⋧": "*",
            "⋨": "*",
            "⋩": "*",
            "⋪": "*",
            "⋫": "*",
            "⋬": "*",
            "⋭": "*",
            "⋮": "*",
            "⋯": "*",
            "⋰": "*",
            "⋱": "*",
            "⋲": "*",
            "⋳": "*",
            "⋴": "*",
            "⋵": "*",
            "⋶": "*",
            "⋷": "*",
            "⋸": "*",
            "⋹": "*",
            "⋺": "*",
            "⋻": "*",
            "⋼": "*",
            "⋽": "*",
            "⋾": "*",
            "⋿": "*",
        }

        # 空白字符模式
        self.whitespace_pattern = re.compile(
            r"[\s\u00A0\u2000-\u200F\u2028-\u202F\u205F-\u206F\u3000]+"
        )

        # 数字映射表
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

    def normalize(self, text: str, preserve_case: bool = False) -> Tuple[str, dict]:
        """
        标准化文本

        Args:
            text: 原始文本
            preserve_case: 是否保留大小写

        Returns:
            normalized_text: 标准化后的文本
            stats: 标准化统计信息
        """
        from collections import Counter

        stats = Counter()
        original_len = len(text)

        # 1. 检测并移除BOM
        if text.startswith("\ufeff"):
            text = text[1:]
            stats["bom_removed"] = 1

        # 2. 统一换行符
        original_newlines = text.count("\r\n") + text.count("\r")
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        stats["newlines_normalized"] = original_newlines

        # 3. 规范化标点符号
        punct_changes = 0
        for old_punct, new_punct in self.punctuation_map.items():
            if old_punct in text:
                count = text.count(old_punct)
                text = text.replace(old_punct, new_punct)
                punct_changes += count
        stats["punctuation_normalized"] = punct_changes

        # 4. 规范化数字
        number_changes = 0
        for old_num, new_num in self.number_map.items():
            if old_num in text:
                count = text.count(old_num)
                text = text.replace(old_num, new_num)
                number_changes += count
        stats["numbers_normalized"] = number_changes

        # 5. 处理省略号
        ellipsis_count = len(re.findall(r"\.{3,}|。{3,}|…+", text))
        text = re.sub(r"\.{3,}|。{3,}|…+", "...", text)
        stats["ellipsis_normalized"] = ellipsis_count

        # 6. 处理重复的标点符号
        text = re.sub(r"([!?]){2,}", r"\1", text)  # 处理多余的感叹号和问号
        text = re.sub(r"(\.{3})[.]+", r"\1", text)  # 处理超过三个点的省略号

        # 7. 标准化空白字符（保留换行符）
        # 只替换空格和制表符，保留换行符
        text = re.sub(r"[ \t\u00A0\u2000-\u200F\u2028-\u202F\u205F-\u206F\u3000]+", " ", text)

        # 8. 转换为小写（如果不保留大小写）
        if not preserve_case:
            text = text.lower()
            stats["case_normalized"] = 1

        # 9. 清理多余空格（保留换行符）
        # 将多个连续空格替换为单个空格，但保留换行符
        text = re.sub(r"[ \t]+", " ", text)  # 只替换空格和制表符
        text = re.sub(r" \n", "\n", text)  # 清理行尾空格
        text = re.sub(r"\n ", "\n", text)  # 清理行首空格
        text = text.strip()

        # 计算总体变化
        stats["total_changes"] = original_len - len(text)

        return text, dict(stats)

    def extract_words(self, text: str) -> list:
        """
        从标准化文本中提取词汇

        Args:
            text: 标准化后的文本

        Returns:
            words: 词汇列表
        """
        # 使用正则表达式提取英文单词
        words = re.findall(r"\b[a-zA-Z]+\b", text)
        return words

    def get_word_positions(self, text: str) -> list:
        """
        获取每个词汇在文本中的位置信息

        Args:
            text: 标准化后的文本

        Returns:
            positions: 位置信息列表，每个元素包含 (word, start, end, line)
        """
        positions = []
        lines = text.split("\n")

        for line_num, line in enumerate(lines, 1):
            for match in re.finditer(r"\b[a-zA-Z]+\b", line):
                word = match.group()
                start = match.start()
                end = match.end()
                positions.append(
                    {
                        "word": word,
                        "start": start,
                        "end": end,
                        "line": line_num,
                        "column": start + 1,
                    }
                )

        return positions

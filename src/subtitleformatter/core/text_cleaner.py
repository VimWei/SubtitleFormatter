import re


class TextCleaner:
    """
    基础文本清理类，用于统一空白字符、换行符、标点符号并清理多余空行
    
    ⚠️ 已弃用：此功能已迁移到插件系统
    请使用 plugins/builtin/text_cleaning 插件替代
    保留此类仅为向后兼容旧的 TextProcessor
    
    For new code, use PluginTextProcessor with text_cleaning plugin instead.
    """

    def __init__(self):
        """初始化文本清理器（已弃用 - 使用插件系统）"""
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

    def process(self, text):
        """执行基础文本清理

        Args:
            text: 原始文本

        Returns:
            cleaned_text: 清理后的文本
            stats: 清理统计信息
        """
        from collections import Counter

        stats = Counter()
        original_len = len(text)

        # 1. 检测并移除 BOM
        if text.startswith("\ufeff"):
            text = text[1:]
            stats["special_chars"] = 1

        # 2. 统一换行符为 \n
        original_newlines = len(text)
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        stats["newlines"] = original_newlines - len(text)

        # 3. 规范化标点符号
        original_punct = len(text)
        for old, new in self.punctuation_map.items():
            text = text.replace(old, new)
        stats["punctuation"] = original_punct - len(text)

        # 4. 规范化数字（全角转半角）
        original_numbers = len(text)
        for old, new in self.number_map.items():
            text = text.replace(old, new)
        stats["numbers"] = original_numbers - len(text)

        # 5. 处理省略号
        text = re.sub(r"\.{3,}|。{3,}|…+", "...", text)

        # 6. 处理重复的标点符号
        text = re.sub(r"([!?]){2,}", r"\1", text)  # 处理多余的感叹号和问号
        text = re.sub(r"(\.{3})[.]+", r"\1", text)  # 处理超过三个点的省略号

        # 7. 将所有特殊空白字符统一转换为普通空格
        text = re.sub(self.whitespace_pattern, " ", text)
        stats["spaces"] = original_len - len(text) - stats["newlines"]

        # 8. 处理中英文之间的空格
        text = re.sub(r"([\u4e00-\u9fff])([a-zA-Z])", r"\1 \2", text)  # 中文后面的英文
        text = re.sub(r"([a-zA-Z])([\u4e00-\u9fff])", r"\1 \2", text)  # 英文后面的中文

        # 9. 确保标点符号后面有空格（有助于 spaCy 识别）
        text = re.sub(r"([,:;.!?])([\u4e00-\u9fff])", r"\1 \2", text)

        # 10. 处理括号内的空格
        text = re.sub(r"\( +", "(", text)
        text = re.sub(r" +\)", ")", text)

        # 11. 删除行末空白
        text = self._clean_line_endings(text)

        # 12. 合并多个空格为单个空格
        text = self._normalize_spaces(text)

        # 13. 确保句子边界清晰
        text = re.sub(r"([.!?])\s*([A-Z])", r"\1\n\2", text)

        # 14. 删除多余的空行，确保段落间有统一的空行
        original_empty_lines = text.count("\n\n")
        text = self._clean_empty_lines(text)
        stats["empty_lines"] = original_empty_lines - text.count("\n\n")

        return text, stats

    def _clean_line_endings(self, text):
        """删除行末空白"""
        lines = text.splitlines()
        lines = [line.rstrip() for line in lines]
        return "\n".join(lines)

    def _normalize_spaces(self, text):
        """合并多个空格为单个空格"""
        return re.sub(r" +", " ", text)

    def _clean_empty_lines(self, text):
        """删除多余的空行，保留单个空行"""
        text = re.sub(r"\n\s*\n", "\n\n", text)  # 将多个空行统一为一个空行
        return text.strip()

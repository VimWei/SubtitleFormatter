"""
SentenceSplitterPlugin - 句子拆分插件

这个插件将长句和复合句拆分为更短的句子，支持：
- 基于规则和启发式方法的智能拆分
- 连接词和标点符号识别
- 递归处理复杂长句
- 上下文感知，避免误拆分
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from subtitleformatter.plugins.base import TextProcessorPlugin


class SentenceSplitterPlugin(TextProcessorPlugin):
    """
    句子拆分插件

    将长句和复合句拆分为更短的句子
    """

    # 插件元数据
    name = "builtin/sentence_splitter"
    version = "1.0.0"
    description = "句子拆分插件，将长句和复合句拆分为更短的句子"
    author = "SubtitleFormatter Team"
    dependencies = []

    # 配置模式
    config_schema = {
        "required": [],
        "optional": {
            "enabled": bool,
            "min_recursive_length": int,
            "max_depth": int,
            "max_degradation_round": int,
        },
        "field_types": {
            "enabled": bool,
            "min_recursive_length": int,
            "max_depth": int,
            "max_degradation_round": int,
        },
    }

    def __init__(self, config: Dict[str, Any] = None):
        """初始化句子拆分插件"""
        super().__init__(config)

        # 应用默认配置
        self.enabled = self.config.get("enabled", True)
        self.min_recursive_length = self.config.get("min_recursive_length", 70)
        self.max_depth = self.config.get("max_depth", 8)
        self.max_degradation_round = self.config.get("max_degradation_round", 5)

        # 连接词列表 - 用于识别复合句的拆分点
        self.conjunctions = {
            # 并列连接词
            "and",
            "or",
            "but",
            "yet",
            "so",
            "for",
            "nor",
            # 从属连接词
            "because",
            "since",
            "as",
            "if",
            "when",
            "while",
            "although",
            "though",
            "unless",
            "until",
            "before",
            "after",
            # 其他连接词
            "however",
            "therefore",
            "moreover",
            "furthermore",
            "nevertheless",
            "meanwhile",
            "consequently",
            "additionally",
            "similarly",
            "likewise",
            "otherwise",
            "instead",
            "rather",
            "indeed",
            # 从句引导词
            "which",
            "that",
            "who",
            "whom",
            "whose",
            "where",
            "when",
            "why",
            "how",
            # 时间/条件连接词
            "then",
            "next",
            "finally",
            "meanwhile",
            "subsequently",
            # 短语连接词
            "such as",
            "as well as",
            "in order to",
            "so that",
            "in case",
            "provided that",
            "even though",
            "as though",
            "as if",
        }

        # 固定短语模式定义（用于保护不被拆分）
        self.fixed_phrases = {
            "so that": {"start_words": ["so"], "end_words": ["that"], "length": 8},
            "provided that": {"start_words": ["provided"], "end_words": ["that"], "length": 13},
            "as though": {"start_words": ["as"], "end_words": ["though"], "length": 9},
            "as if": {"start_words": ["as"], "end_words": ["if"], "length": 6},
            "even though": {"start_words": ["even"], "end_words": ["though"], "length": 12},
            "such as": {"start_words": ["such"], "end_words": ["as"], "length": 8},
            "as well as": {"start_words": ["as"], "end_words": ["as"], "length": 9},
            "in order to": {"start_words": ["in"], "end_words": ["to"], "length": 11},
            "in case": {"start_words": ["in"], "end_words": ["case"], "length": 7},
        }

        # 标点符号优先级（用于确定最佳拆分点）
        self.punctuation_priority = {
            ";": 5,  # 分号优先级最高
            ":": 4,  # 冒号次之
            ",": 3,  # 逗号第三
            "—": 3,  # 长破折号
            "–": 3,  # 短破折号
            "…": 3,  # 省略号
        }

        # 连接词优先级
        self.conjunction_priority = {
            # 高优先级连接词
            "however": 2,
            "therefore": 2,
            "moreover": 2,
            "furthermore": 2,
            "nevertheless": 2,
            "meanwhile": 2,
            "consequently": 2,
            # 转折连接词（高优先级）
            "but": 2,
            "yet": 2,
            # 中优先级连接词
            "because": 1,
            "since": 1,
            "although": 1,
            "though": 1,
            "unless": 1,
            "until": 1,
            "before": 1,
            "after": 1,
            "as": 1,
            "if": 1,
            "while": 1,
            # 从句引导词（中等优先级）
            "that": 1,
            "which": 1,
            "who": 1,
            "whom": 1,
            "whose": 1,
            "where": 1,
            "when": 1,
            "why": 1,
            "how": 1,
            # 其他连接词（中等优先级）
            "additionally": 1,
            "similarly": 1,
            "likewise": 1,
            "otherwise": 1,
            "instead": 1,
            "rather": 1,
            "indeed": 1,
            # 低优先级连接词
            "and": 0,
            "or": 0,
            "so": 0,
            "for": 0,
            "nor": 0,
            "then": 0,
            "next": 0,
            "finally": 0,
            "subsequently": 0,
            "even": 0,
            # 短语连接词（低优先级）
            "such as": 0,
            "as well as": 0,
            "in order to": 0,
            "so that": 0,
            "in case": 0,
            "provided that": 0,
            "even though": 0,
            "as though": 0,
            "as if": 0,
        }

        # 数字模式（用于排除数字分隔符）
        self.number_patterns = [
            r"\d{1,3}(,\d{3})+",  # 1,000 或 1,000,000
            r"\d+\.\d+",  # 小数
        ]

        # 简单并列模式（用于排除简单词汇并列）
        self.simple_enumeration_patterns = [
            r"\b\w+,\s*\w+,\s*\w+\b",  # apple, banana, orange
        ]

    def process(self, text: Union[str, List[str]]) -> List[str]:
        """
        执行句子拆分处理

        Args:
            text: 原始文本（字符串或字符串列表）

        Returns:
            处理后的句子列表
        """
        if not self.enabled:
            return [text] if isinstance(text, str) else text

        # 处理输入类型
        if isinstance(text, list):
            result = []
            for item in text:
                result.extend(self._process_single_text_as_list(item))
            return result
        else:
            # 对于字符串输入，返回列表
            return self._process_single_text_as_list(text)

    def _process_single_text(self, text: str) -> str:
        """
        处理单个文本

        Args:
            text: 原始文本

        Returns:
            处理后的文本（每行一个拆分后的句子）
        """
        if not text or not isinstance(text, str):
            return text

        # 将文本按行分割（每行一个句子）
        lines = text.strip().split("\n")
        all_sentences = []

        for line in lines:
            line = line.strip()
            if line:
                all_sentences.append(line)

        # 处理句子列表
        processed_sentences = self.process_sentences(all_sentences)

        # 返回每行一个句子的格式
        return "\n".join(processed_sentences)

    def _process_single_text_as_list(self, text: str) -> List[str]:
        """
        处理单个文本并返回列表

        Args:
            text: 原始文本

        Returns:
            处理后的句子列表
        """
        if text is None:
            return [None]
        if not isinstance(text, str) or not text.strip():
            return []

        # 将文本按行分割（每行一个句子）
        lines = text.strip().split("\n")
        all_sentences = []

        for line in lines:
            line = line.strip()
            if line:
                all_sentences.append(line)

        # 处理句子列表
        processed_sentences = self.process_sentences(all_sentences)

        return processed_sentences

    def _is_in_fixed_phrase(self, sentence: str, pos: int, conjunction: str) -> bool:
        """
        检查连接词是否在固定短语中

        Args:
            sentence: 完整句子
            pos: 连接词位置
            conjunction: 连接词

        Returns:
            bool: 如果在固定短语中返回True，否则返回False
        """
        sentence_lower = sentence.lower()

        # 遍历所有固定短语模式
        for phrase, pattern in self.fixed_phrases.items():
            start_words = pattern["start_words"]
            end_words = pattern["end_words"]
            phrase_length = pattern["length"]

            # 检查当前连接词是否是固定短语的起始词
            if conjunction in start_words:
                # 检查从当前位置开始的短语是否匹配
                if pos + phrase_length <= len(sentence_lower):
                    if sentence_lower[pos : pos + phrase_length].startswith(phrase):
                        return True

            # 检查当前连接词是否是固定短语的结束词
            elif conjunction in end_words:
                # 检查前面是否有匹配的起始词
                for start_word in start_words:
                    start_pos = pos - len(start_word) - 1  # -1 for space
                    if start_pos >= 0:
                        # 检查是否匹配固定短语
                        if start_pos + phrase_length <= len(sentence_lower):
                            if sentence_lower[start_pos : start_pos + phrase_length].startswith(
                                phrase
                            ):
                                return True

        return False

    def is_number_context(self, text: str, pos: int) -> bool:
        """检查逗号是否在数字上下文中"""

        # 获取逗号前后的内容
        before = text[:pos].rstrip()
        after = text[pos + 1 :].lstrip()

        # 检查逗号前后是否都是数字（千位分隔符情况）
        if before and after:
            # 检查逗号前是否有数字结尾
            before_match = re.search(r"\d+$", before)
            # 检查逗号后是否有数字开头
            after_match = re.search(r"^\d+", after)

            if before_match and after_match:
                return True

        # 检查是否在货币格式中（如 $3,000, €1,000, £500 等）
        if pos > 0:
            # 检查逗号前是否有货币符号
            currency_symbols = [
                "$",
                "€",
                "£",
                "¥",
                "₹",
                "₽",
                "₩",
                "₪",
                "₨",
                "₦",
                "₡",
                "₱",
                "₫",
                "₴",
                "₸",
                "₼",
                "₾",
                "₿",
            ]
            if text[pos - 1] in currency_symbols:
                # 检查逗号后是否有数字
                after_match = re.search(r"^\d+", after)
                if after_match:
                    return True

        # 检查是否在数字模式中（如 1,000,000 或 3,000）
        # 使用更精确的正则表达式检查逗号是否在数字中间
        context = text[max(0, pos - 10) : pos + 10]
        number_patterns = [
            r"\d{1,3}(,\d{3})+",  # 千位分隔符：1,000 或 1,000,000
            r"\d+,\d{3}",  # 简单千位分隔符：3,000
        ]

        for pattern in number_patterns:
            if re.search(pattern, context):
                return True

        return False

    def is_simple_enumeration(self, text: str, pos: int) -> bool:
        """检查逗号是否在简单并列中 - 仅基于词汇数量判断"""
        # 首先检查是否在数字上下文中，如果是则不认为是简单并列
        if self.is_number_context(text, pos):
            return False

        # 获取逗号前后的词汇
        before_text = text[:pos].strip()
        after_text = text[pos + 1 :].strip()

        # 提取逗号前后的词汇（去除标点）
        before_words = re.findall(r"\b\w+\b", before_text)
        after_words = re.findall(r"\b\w+\b", after_text)

        # 简单判断：如果逗号前后都只有1-2个词汇，且总词汇数不超过6个，则认为是简单并列
        total_words = len(before_words) + len(after_words)
        if total_words <= 6 and len(before_words) <= 2 and len(after_words) <= 2:
            return True

        return False

    def _is_in_subordinate_clause(self, sentence: str, pos: int) -> bool:
        """检查位置是否在从句中"""

        # 查找最近的从句引导词
        subordinate_markers = [
            "which",
            "that",
            "who",
            "whom",
            "whose",
            "where",
            "when",
            "why",
            "how",
        ]

        # 检查位置前是否有从句引导词
        before_pos = sentence[:pos].lower()
        for marker in subordinate_markers:
            marker_pos = before_pos.rfind(marker)
            if marker_pos != -1:
                # 检查从句引导词前是否有逗号
                before_marker = sentence[:marker_pos]
                if "," in before_marker:
                    # 这是一个从句，检查位置是否在从句内部
                    # 如果位置在从句引导词之后，则认为在从句中
                    if pos > marker_pos:
                        return True

        return False

    def _is_valid_split_point(self, sentence: str, pos: int, round_num: int = 1) -> bool:
        """
        拆分点有效性检查（支持逐步退化）
        round_num: 1=正常, 2=移除从句检测, 3=移除简单并列检测, 4=降低长度要求, 5=移除所有限制
        """
        # 根据轮次设置最小长度要求
        if round_num >= 4:
            min_length = 10  # 第4轮：降低长度要求
        else:
            min_length = 15  # 第1-3轮：正常长度要求

        # 统一处理所有标点符号，计算实际拆分位置
        actual_pos = pos
        if 0 <= pos < len(sentence):
            # 定义所有需要统一处理的标点符号
            punctuation_marks = {",", ":", ";", ".", "!", "?", "—", "–", "…"}

            if sentence[pos] in punctuation_marks:
                # 对于逗号，需要特殊处理从句引导词
                if sentence[pos] == ",":
                    # 检查逗号后是否跟着从句引导词
                    after_comma = sentence[pos + 1 :].strip()
                    subordinate_markers = [
                        "that",
                        "which",
                        "who",
                        "whom",
                        "whose",
                        "where",
                        "when",
                        "why",
                        "how",
                    ]
                    is_subordinate = any(
                        after_comma.lower().startswith(marker + " ")
                        for marker in subordinate_markers
                    )

                    if is_subordinate:
                        # 从句：跳过逗号和空格，让从句引导词在下一行开头
                        actual_pos += 1
                        if actual_pos < len(sentence) and sentence[actual_pos] == " ":  # 跳过空格
                            actual_pos += 1
                    else:
                        # 非从句：跳过逗号和空格
                        actual_pos += 1
                        if (
                            actual_pos < len(sentence) and sentence[actual_pos] == " "
                        ):  # 保留一个空格在上一行
                            actual_pos += 1
                else:
                    # 其他标点符号：统一跳过标点符号和其后的空格
                    actual_pos += 1
                    if actual_pos < len(sentence) and sentence[actual_pos] == " ":  # 跳过空格
                        actual_pos += 1
            elif sentence[pos] == " " and pos > 0:
                # 如果正好在标点符号后的空格处分行，则跳过这个空格
                if sentence[pos - 1] in punctuation_marks:
                    actual_pos += 1

        # 使用实际拆分位置计算长度
        part1 = sentence[:actual_pos].strip()
        part2 = sentence[actual_pos:].strip()

        if len(part1) < min_length or len(part2) < min_length:
            return False

        # 第3轮及以后：移除简单并列检测
        if round_num < 3:
            if sentence[pos] == "," and self.is_simple_enumeration(sentence, pos):
                return False

        # 第1轮：检查从句（第2轮及以后不检查）
        if round_num == 1:
            if self._is_in_subordinate_clause(sentence, pos):
                return False

        return True

    def find_split_points(self, sentence: str, round_num: int = 1) -> List[Tuple[int, int, str]]:
        """
        拆分点查找（支持逐步退化）
        round_num: 1=正常, 2=移除从句检测, 3=移除简单并列检测, 4=降低长度要求, 5=移除所有限制
        """
        split_points = []

        # 查找标点符号拆分点（简化版本）
        for punct, priority in self.punctuation_priority.items():
            for match in re.finditer(re.escape(punct), sentence):
                pos = match.start()

                # 排除数字上下文中的逗号
                if punct == "," and self.is_number_context(sentence, pos):
                    continue

                # 逗号特殊处理
                if punct == ",":
                    after_comma = sentence[pos + 1 :].strip()
                    found_conjunction = False

                    # 检查逗号后的连接词
                    elevated_after = {
                        "that",
                        "which",
                        "who",
                        "whom",
                        "whose",
                        "where",
                        "when",
                        "why",
                        "how",
                    }
                    # 转折连接词获得更高优先级
                    contrast_conjunctions = {"but", "yet"}

                    for conjunction in self.conjunctions:
                        if after_comma.lower().startswith(conjunction + " "):
                            if conjunction in elevated_after:
                                boost = 6
                            elif conjunction in contrast_conjunctions:
                                boost = 4  # 转折连接词优先级高于普通连接词
                            else:
                                boost = 2
                            split_points.append(
                                (pos, priority + boost, f"逗号+连接词: {conjunction}")
                            )
                            found_conjunction = True
                            break

                    if not found_conjunction:
                        # 检查逗号模式
                        comma_patterns = [
                            r",\s+(that|which|who|whom|whose|where|when|why|how)\s+",
                            r",\s+(and|or|but|so|yet|for|nor)\s+",
                            r",\s+(however|therefore|moreover|furthermore|meanwhile)\s+",
                        ]

                        for pattern in comma_patterns:
                            if re.search(pattern, sentence[pos : pos + 50], re.IGNORECASE):
                                if re.match(
                                    r",\s+(that|which|who|whom|whose|where|when|why|how)\s+",
                                    sentence[pos : pos + 50],
                                    re.IGNORECASE,
                                ):
                                    split_points.append(
                                        (pos, priority + 6, f"逗号+从句: {pattern}")
                                    )
                                else:
                                    split_points.append(
                                        (pos, priority + 2, f"逗号+模式: {pattern}")
                                    )
                                found_conjunction = True
                                break

                    if not found_conjunction:
                        # 普通逗号拆分
                        split_points.append((pos, priority, f"标点符号: {punct}"))
                else:
                    split_points.append((pos, priority, f"标点符号: {punct}"))

        # 连接词拆分（退化版本 - 降低长度要求）
        for conjunction in self.conjunctions:
            sentence_lower = sentence.lower()
            pos = 0
            while True:
                pos = sentence_lower.find(conjunction, pos)
                if pos == -1:
                    break

                # 检查是否在固定短语中，如果是则跳过
                if self._is_in_fixed_phrase(sentence, pos, conjunction):
                    pos += len(conjunction)  # 跳过当前连接词，继续查找
                    continue

                # 确保是完整的单词
                if (
                    pos > 0
                    and (pos == 0 or not sentence_lower[pos - 1].isalnum())
                    and (
                        pos + len(conjunction) >= len(sentence_lower)
                        or not sentence_lower[pos + len(conjunction)].isalnum()
                    )
                ):
                    # 简单处理：如果 that 后面是逗号，则不是有效的拆分点
                    if conjunction == "that":
                        if pos + 4 < len(sentence) and sentence[pos + 4] == ",":
                            pos += len(conjunction)
                            continue

                    # 根据轮次设置长度要求
                    before_conjunction = sentence[:pos].strip()
                    after_conjunction = sentence[pos + len(conjunction) :].strip()

                    # 长度要求：第4-5轮降低到10字符，其他轮次保持20字符
                    if round_num >= 4:
                        min_length = 10
                    else:
                        min_length = 20

                    if len(before_conjunction) > min_length and len(after_conjunction) > min_length:
                        # 第2轮：移除从句检测
                        if round_num >= 2:
                            # 不检查从句，直接添加
                            priority = self.conjunction_priority.get(conjunction, 0)
                            split_points.append((pos, priority, f"连接词: {conjunction}"))
                        else:
                            # 第1轮：正常检查从句
                            if not self._is_in_subordinate_clause(sentence, pos):
                                priority = self.conjunction_priority.get(conjunction, 0)
                                split_points.append((pos, priority, f"连接词: {conjunction}"))

                pos += len(conjunction)

        # 按位置排序
        split_points.sort(key=lambda x: x[0])
        return split_points

    def find_best_split(self, sentence: str) -> Optional[Tuple[int, str, str, int]]:
        """拆分点查找（支持逐步退化）"""
        # 确定最大退化轮次
        max_round = min(self.max_degradation_round, 5)

        # 第1轮：正常策略
        split_points = self.find_split_points(sentence)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=1):
                    # 将优先级转换为字符串类型
                    split_type = self._priority_to_type(priority, reason)
                    valid_splits.append((pos, priority, reason, split_type))

            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[3], best[2], 1)  # 返回 (pos, split_type, reason, round)

        if max_round < 2:
            return None

        # 第2轮：移除从句检测
        split_points = self.find_split_points(sentence, round_num=2)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=2):
                    split_type = self._priority_to_type(priority, reason)
                    valid_splits.append((pos, priority, reason, split_type))

            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[3], best[2], 2)

        if max_round < 3:
            return None

        # 第3轮：移除简单并列检测
        split_points = self.find_split_points(sentence, round_num=3)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=3):
                    split_type = self._priority_to_type(priority, reason)
                    valid_splits.append((pos, priority, reason, split_type))

            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[3], best[2], 3)

        if max_round < 4:
            return None

        # 第4轮：降低长度要求
        split_points = self.find_split_points(sentence, round_num=4)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=4):
                    split_type = self._priority_to_type(priority, reason)
                    valid_splits.append((pos, priority, reason, split_type))

            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[3], best[2], 4)

        if max_round < 5:
            return None

        # 第5轮：移除所有限制
        split_points = self.find_split_points(sentence, round_num=5)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=5):
                    split_type = self._priority_to_type(priority, reason)
                    valid_splits.append((pos, priority, reason, split_type))

            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[3], best[2], 5)

        # 如果所有轮次后仍然找不到有效拆分点，返回None
        return None

    def should_split_sentence(self, sentence: str) -> bool:
        """判断句子是否需要拆分"""
        # 长度阈值
        if len(sentence) < self.min_recursive_length:  # 与递归拆分条件保持一致
            return False

        # 检查是否包含不应该拆分的模式（已移除特例化规则，统一走长度/优先级策略）
        problematic_patterns = []

        for pattern in problematic_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return False

        # 检查是否有拆分点
        split_points = self.find_split_points(sentence, round_num=1)
        if len(split_points) > 0:
            return True

        # 兜底规则：如果没有找到拆分点，但句子中间有逗号，且拆分后两部分都不太短，则允许拆分
        comma_matches = list(re.finditer(r",", sentence))
        if len(comma_matches) > 0:
            # 排除句末的逗号（逗号后直接跟着句末标点）
            for match in comma_matches:
                pos = match.start()
                # 检查逗号后是否还有内容（不是句末逗号）
                after_comma = sentence[pos + 1 :].strip()
                if after_comma:
                    # 检查是否是句末逗号：逗号后只有很少内容且以句末标点结尾
                    after_comma_no_space = after_comma.lstrip()
                    if (
                        after_comma_no_space and len(after_comma_no_space) > 10
                    ):  # 逗号后有足够的内容
                        # 检查拆分后的两部分长度
                        part1 = sentence[:pos].strip()
                        part2 = after_comma
                        if len(part1) >= 20 and len(part2) >= 20:  # 两部分都不太短
                            return True

        return False

    def _priority_to_type(self, priority: int, reason: str) -> str:
        """
        将优先级和原因转换为字符串类型的拆分类型

        Args:
            priority: 优先级数值
            reason: 拆分原因

        Returns:
            字符串类型的拆分类型
        """
        # 根据reason内容判断拆分类型
        if "连接词" in reason or "conjunction" in reason.lower():
            return "conjunction"
        elif "标点" in reason or "punctuation" in reason.lower():
            return "punctuation"
        elif "介词" in reason or "preposition" in reason.lower():
            return "preposition"
        elif "从句" in reason or "subordinate" in reason.lower():
            return "subordinate"
        else:
            return "fallback"

    def split_sentence(self, sentence: str, depth: int = 0) -> List[str]:
        """拆分单个句子"""
        # 递归停止条件：深度超限或长度不足
        if depth >= self.max_depth or len(sentence) < self.min_recursive_length:
            return [sentence]

        if not self.should_split_sentence(sentence):
            return [sentence]

        # 使用带兜底方案的拆分点查找
        best_split = self.find_best_split(sentence)

        if best_split is None:
            # 如果找不到有效拆分点，保持原样（留给人工处理）
            if len(sentence) > 100:  # 只对长句输出警告
                self.logger.warning(f"无法拆分长句（长度: {len(sentence)}）: {sentence[:50]}...")
                return [sentence]
            else:
                return [sentence]

        split_pos, priority, reason, round_num = best_split

        # 统一处理所有标点符号：保留标点符号在上一行，跳过其后的空格
        if 0 <= split_pos < len(sentence):
            # 定义所有需要统一处理的标点符号
            punctuation_marks = {",", ":", ";", ".", "!", "?", "—", "–", "…"}

            if sentence[split_pos] in punctuation_marks:
                # 对于逗号，需要特殊处理从句引导词
                if sentence[split_pos] == ",":
                    # 检查逗号后是否跟着从句引导词
                    after_comma = sentence[split_pos + 1 :].strip()
                    subordinate_markers = [
                        "that",
                        "which",
                        "who",
                        "whom",
                        "whose",
                        "where",
                        "when",
                        "why",
                        "how",
                    ]
                    is_subordinate = any(
                        after_comma.lower().startswith(marker + " ")
                        for marker in subordinate_markers
                    )

                    if is_subordinate:
                        # 从句：跳过逗号和空格，让从句引导词在下一行开头
                        split_pos += 1
                        if split_pos < len(sentence) and sentence[split_pos] == " ":  # 跳过空格
                            split_pos += 1
                    else:
                        # 非从句：跳过逗号和空格
                        split_pos += 1
                        if (
                            split_pos < len(sentence) and sentence[split_pos] == " "
                        ):  # 保留一个空格在上一行
                            split_pos += 1
                else:
                    # 其他标点符号：统一跳过标点符号和其后的空格
                    split_pos += 1
                    if split_pos < len(sentence) and sentence[split_pos] == " ":  # 跳过空格
                        split_pos += 1
            elif sentence[split_pos] == " " and split_pos > 0:
                # 如果正好在标点符号后的空格处分行，则跳过这个空格
                if sentence[split_pos - 1] in punctuation_marks:
                    split_pos += 1

        # 拆分句子（不修改任何标点或空白，只做换行）
        part1 = sentence[:split_pos]
        part2 = sentence[split_pos:]

        # 检查拆分后的部分是否太短（避免单个连接词成行）
        # 对于兜底方案，允许更短的后部分
        min_part_length = 8 if round_num >= 4 else 10
        if len(part1.strip()) < min_part_length or len(part2.strip()) < min_part_length:
            return [sentence]

        # 递归拆分：对每个部分独立评估
        result = []
        if part1 and len(part1) >= self.min_recursive_length:
            result.extend(self.split_sentence(part1, depth + 1))
        elif part1:
            result.append(part1)

        if part2 and len(part2) >= self.min_recursive_length:
            result.extend(self.split_sentence(part2, depth + 1))
        elif part2:
            result.append(part2)

        return result if result else [sentence]

    def process_sentences(self, sentences: List[str]) -> List[str]:
        """处理句子列表"""
        result = []
        for sentence in sentences:
            if sentence.strip():
                split_sentences = self.split_sentence(sentence.strip())
                result.extend(split_sentences)
        return result

    def get_split_stats(self, sentences: List[str]) -> Dict[str, Any]:
        """
        获取拆分统计信息

        Args:
            sentences: 输入句子列表

        Returns:
            统计信息字典
        """
        original_count = len(sentences)
        processed_sentences = self.process_sentences(sentences)
        final_count = len(processed_sentences)

        return {
            "original_sentence_count": original_count,
            "final_sentence_count": final_count,
            "split_count": final_count - original_count,
            "split_ratio": final_count / original_count if original_count > 0 else 0,
        }

    def split_sentences(self, sentence: str) -> List[str]:
        """
        兼容性方法：将单个句子拆分为句子列表
        这是测试期望的方法名
        """
        return self.split_sentence(sentence)

    def split_at_position(self, sentence: str, position: int) -> Tuple[str, str]:
        """
        在指定位置拆分句子

        Args:
            sentence: 要拆分的句子
            position: 拆分位置

        Returns:
            (前部分, 后部分) 的元组
        """
        if position <= 0:
            return ("", sentence)
        if position >= len(sentence):
            return (sentence, "")

        return (sentence[:position], sentence[position:])

    def is_valid_split(self, part1: str, part2: str) -> bool:
        """
        检查拆分是否有效

        Args:
            part1: 前部分
            part2: 后部分

        Returns:
            是否有效拆分
        """
        # 基本长度检查
        if len(part1.strip()) < 3 or len(part2.strip()) < 3:
            return False

        # 检查是否包含完整的单词
        if part1.strip() and not part1.strip()[-1].isalnum():
            return False
        if part2.strip() and not part2.strip()[0].isalnum():
            return False

        return True

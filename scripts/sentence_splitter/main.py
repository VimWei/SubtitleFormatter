#!/usr/bin/env python3
"""
句子拆分工具 - 将长句和复合句拆分为更短的句子
基于规则和启发式方法，无需LLM即可实现智能拆分
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple


class SentenceSplitter:
    """句子拆分器"""

    def __init__(self, min_recursive_length: int = 70, max_depth: int = 8):
        # 递归控制参数
        self.min_recursive_length = min_recursive_length  # 最小递归长度阈值
        self.max_depth = max_depth  # 最大递归深度

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
            # 中优先级连接词
            "because": 1,
            "since": 1,
            "although": 1,
            "though": 1,
            "unless": 1,
            "until": 1,
            "before": 1,
            "after": 1,
            "while": 1,
            "when": 1,
            "where": 1,
            "which": 1,
            "that": 1,
            "who": 1,
            "whom": 1,
            "whose": 1,
            "why": 1,
            "how": 1,
            # 转折连接词（高优先级）
            "but": 2,
            "yet": 2,
            # 低优先级连接词
            "and": 0,
            "or": 0,
            "so": 0,
            "for": 0,
            "nor": 0,
            "then": 0,
            "next": 0,
            "finally": 0,
            "meanwhile": 0,
            "subsequently": 0,
            "additionally": 0,
            "similarly": 0,
            "likewise": 0,
            "otherwise": 0,
            "instead": 0,
            "rather": 0,
            "indeed": 0,
            # 短语连接词
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
                    if sentence_lower[pos:pos+phrase_length].startswith(phrase):
                        return True
            
            # 检查当前连接词是否是固定短语的结束词
            elif conjunction in end_words:
                # 检查前面是否有匹配的起始词
                for start_word in start_words:
                    start_pos = pos - len(start_word) - 1  # -1 for space
                    if start_pos >= 0:
                        # 检查是否匹配固定短语
                        if start_pos + phrase_length <= len(sentence_lower):
                            if sentence_lower[start_pos:start_pos+phrase_length].startswith(phrase):
                                return True
        
        return False


        # 标点符号优先级（用于确定最佳拆分点）
        self.punctuation_priority = {
            ";": 5,  # 分号优先级最高
            ":": 4,  # 冒号次之
            ",": 3,  # 逗号第三
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
            # 中优先级连接词
            "because": 1,
            "since": 1,
            "although": 1,
            "though": 1,
            "unless": 1,
            "until": 1,
            "before": 1,
            "after": 1,
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
            # 低优先级连接词
            "and": 0,
            "or": 0,
            "but": 0,
            "yet": 0,
            "so": 0,
            "for": 0,
            "nor": 0,
        }

        # 数字格式模式（用于排除数字中的逗号）
        self.number_patterns = [
            r"\d{1,3}(,\d{3})*",  # 千位分隔符：1,000,000
            r"\d+\.\d+",  # 小数：3.14
            r"\$\d+(,\d{3})*",  # 货币：$1,000
        ]

        # 简单并列模式（用于排除简单的词汇并列）
        self.simple_enumeration_patterns = [
            r"\b\w+\s*,\s*\w+\s*,\s*\w+\b",  # 三个或更多简单词汇并列
            r"\b\w+\s*,\s*(?!and|or|but|yet|so|for|nor|because|since|as|if|when|while|although|though|unless|until|before|after|however|therefore|moreover|furthermore|nevertheless|meanwhile|consequently|additionally|similarly|likewise|otherwise|instead|rather|indeed|which|that|who|whom|whose|where|when|why|how|then|next|finally|subsequently|a|an|the|this|that|these|those|you|we|they|he|she|it|i|me|us|them|him|her|might|could|would|should|will|can|may|must|shall)\w+\b",  # 两个简单词汇并列，但排除连接词、冠词、代词和助动词
        ]

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
        
        # 考虑逗号处理逻辑，计算实际拆分位置
        actual_pos = pos
        if 0 <= pos < len(sentence):
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
                    after_comma.lower().startswith(marker + " ") for marker in subordinate_markers
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
            elif sentence[pos] == ":":
                # 冒号：跳过冒号和空格，让后续内容在下一行开头
                actual_pos += 1
                if actual_pos < len(sentence) and sentence[actual_pos] == " ":  # 跳过空格
                    actual_pos += 1
            elif sentence[pos] == " " and pos > 0 and sentence[pos - 1] == ",":
                # 如果正好在逗号后的空格处分行，则跳过这个空格
                actual_pos += 1
            elif sentence[pos] == " " and pos > 0 and sentence[pos - 1] == ":":
                # 如果正好在冒号后的空格处分行，则跳过这个空格
                actual_pos += 1
        
        # 使用实际拆分位置计算长度
        part1 = sentence[:actual_pos].strip()
        part2 = sentence[actual_pos:].strip()
        
        if len(part1) < min_length or len(part2) < min_length:
            return False
        
        # 检查数字上下文（所有轮次都检查）
        if sentence[pos] == "," and self.is_number_context(sentence, pos):
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
                        "that", "which", "who", "whom", "whose", 
                        "where", "when", "why", "how"
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
                    
                    # 长度要求：第5轮降低到5字符，第4轮降低到10字符，其他轮次保持20字符
                    if round_num >= 5:
                        min_length = 5
                    elif round_num >= 4:
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

    def find_best_split(self, sentence: str) -> Optional[Tuple[int, int, str, int]]:
        """拆分点查找（支持逐步退化）"""
        # 第1轮：正常策略
        split_points = self.find_split_points(sentence)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=1):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[1], best[2], 1)  # 添加轮次信息
        
        # 第2轮：移除从句检测
        split_points = self.find_split_points(sentence, round_num=2)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=2):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[1], best[2], 2)
        
        # 第3轮：移除简单并列检测
        split_points = self.find_split_points(sentence, round_num=3)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=3):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[1], best[2], 3)
        
        # 第4轮：降低长度要求
        split_points = self.find_split_points(sentence, round_num=4)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=4):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[1], best[2], 4)
        
        # 第5轮：移除所有限制
        split_points = self.find_split_points(sentence, round_num=5)
        if split_points:
            valid_splits = []
            for pos, priority, reason in split_points:
                if self._is_valid_split_point(sentence, pos, round_num=5):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 按优先级排序，选择最佳拆分点
                best = max(valid_splits, key=lambda x: (x[1], -x[0]))
                return (best[0], best[1], best[2], 5)
        
        # 如果5轮弱化后仍然找不到有效拆分点，返回None
        return None


    def should_split_sentence(self, sentence: str) -> bool:
        """判断句子是否需要拆分"""
        # 长度阈值
        if len(sentence) < 60:  # 进一步降低长度阈值
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
        import re

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
                print(f"⚠️  无法拆分长句（长度: {len(sentence)}）: {sentence[:50]}...")
            return [sentence]
        
        split_pos, priority, reason, round_num = best_split

        # 若在逗号处分行，确保将逗号与其后的一个空格保留在上一行
        if 0 <= split_pos < len(sentence):
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
                    after_comma.lower().startswith(marker + " ") for marker in subordinate_markers
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
            elif sentence[split_pos] == ":":
                # 冒号：跳过冒号和空格，让后续内容在下一行开头
                split_pos += 1
                if split_pos < len(sentence) and sentence[split_pos] == " ":  # 跳过空格
                    split_pos += 1
            elif sentence[split_pos] == " " and split_pos > 0 and sentence[split_pos - 1] == ",":
                # 如果正好在逗号后的空格处分行，则跳过这个空格
                split_pos += 1
            elif sentence[split_pos] == " " and split_pos > 0 and sentence[split_pos - 1] == ":":
                # 如果正好在冒号后的空格处分行，则跳过这个空格
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

    def process_file(self, input_file: Path, output_file: Path = None) -> None:
        """处理文件"""
        try:
            # 读取输入文件
            with open(input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            # 处理每一行（每行一个句子）
            all_sentences = []
            for line in lines:
                line = line.strip()
                if line:
                    all_sentences.append(line)

            # 智能拆分
            processed_sentences = self.process_sentences(all_sentences)

            # 如果没有指定输出文件，自动生成
            if output_file is None:
                input_stem = input_file.stem
                output_file = Path("data/output") / f"{input_stem}.split.txt"
                output_file.parent.mkdir(parents=True, exist_ok=True)

            # 写入输出文件
            with open(output_file, "w", encoding="utf-8") as f:
                for sentence in processed_sentences:
                    # 清除行尾空格
                    cleaned_sentence = sentence.rstrip()
                    f.write(cleaned_sentence + "\n")

            print(f"✅ 处理完成:")
            print(f"   原始句子数: {len(all_sentences)}")
            print(f"   拆分后句子数: {len(processed_sentences)}")
            print(f"   输出文件: {output_file}")

        except FileNotFoundError:
            print(f"❌ 错误：找不到输入文件 {input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="句子拆分工具 - 将长句和复合句拆分为更短的句子",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py input.txt                    # 自动保存到 data/output/
  python main.py input.txt -o output.txt      # 自定义输出文件
  python main.py input.txt --output output.txt # 自定义输出文件

功能特点:
  - 基于规则和启发式方法，无需LLM
  - 识别连接词和标点符号进行智能拆分
  - 排除数字格式和简单并列的误拆分
  - 支持递归拆分，处理复杂复合句
        """,
    )

    parser.add_argument("input_file", help="输入文本文件路径（每行一个句子）")
    parser.add_argument(
        "-o", "--output", dest="output_file", help="输出文件路径（可选，不指定则自动生成）"
    )
    parser.add_argument(
        "--min-length",
        type=int,
        default=70,
        help="最小递归长度阈值（默认70，低于此长度不再递归拆分）",
    )
    parser.add_argument(
        "--max-depth", type=int, default=8, help="最大递归深度（默认8，防止过度递归）"
    )
    parser.add_argument("--version", action="version", version="句子拆分工具 v1.0.0")

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
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建拆分器并处理文件
    splitter = SentenceSplitter(min_recursive_length=args.min_length, max_depth=args.max_depth)
    splitter.process_file(input_path, output_path)


if __name__ == "__main__":
    main()

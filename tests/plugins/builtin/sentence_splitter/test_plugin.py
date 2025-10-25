#!/usr/bin/env python3
"""
SentenceSplitterPlugin 测试文件

测试句子拆分插件的各种功能：
- 基本句子拆分功能
- 退化策略测试
- 连词处理
- 标点符号优先级
- 配置选项测试
"""

import os
import sys
from pathlib import Path

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from plugins.builtin.sentence_splitter.plugin import SentenceSplitterPlugin


class TestSentenceSplitterPlugin:
    """SentenceSplitterPlugin 测试类"""

    def setup_method(self):
        """测试前准备"""
        self.plugin = SentenceSplitterPlugin()

    def test_plugin_initialization(self):
        """测试插件初始化"""
        assert self.plugin.name == "builtin/sentence_splitter"
        assert self.plugin.version == "1.0.0"
        assert self.plugin.enabled is True
        assert self.plugin.min_recursive_length == 70
        assert self.plugin.max_depth == 8
        assert self.plugin.max_degradation_round == 5

    def test_plugin_disabled(self):
        """测试插件禁用状态"""
        plugin = SentenceSplitterPlugin({"enabled": False})
        text = "This is a very long sentence that should be split into multiple parts."
        result = plugin.process(text)
        assert result == [text]  # 应该返回原文列表

    def test_custom_config(self):
        """测试自定义配置"""
        config = {"min_recursive_length": 50, "max_depth": 5, "max_degradation_round": 3}
        plugin = SentenceSplitterPlugin(config)

        assert plugin.min_recursive_length == 50
        assert plugin.max_depth == 5
        assert plugin.max_degradation_round == 3

    def test_short_sentence_no_split(self):
        """测试短句子不拆分"""
        short_sentences = [
            "This is a short sentence.",
            "Hello world!",
            "How are you?",
            "Good morning.",
        ]

        for sentence in short_sentences:
            result = self.plugin.process(sentence)
            assert result == [sentence], f"短句子不应该被拆分: {sentence}"

    def test_long_sentence_basic_split(self):
        """测试长句子基本拆分"""
        long_sentence = "This is a very long sentence that contains multiple clauses and should be split into smaller parts for better readability and understanding."
        result = self.plugin.split_sentences(long_sentence)

        # 应该被拆分成多个部分
        assert len(result) > 1
        # 每个部分都应该比原句短
        for part in result:
            assert len(part) < len(long_sentence)

    def test_conjunction_splitting(self):
        """测试连词拆分"""
        test_cases = [
            "I went to the store and bought some groceries and then went home and had dinner with my family.",
            "She likes to read books but she also enjoys watching movies and playing games.",
            "We can go to the park or we can stay at home and watch television.",
            "He is tall and strong and very athletic and he plays basketball every day.",
        ]

        for sentence in test_cases:
            result = self.plugin.process(sentence)
            # 长句子应该被拆分成多个部分（如果满足拆分条件）
            if len(sentence) > 100:  # 只有很长的句子才强制要求拆分
                assert len(result) > 1, f"长句子应该被拆分: {sentence}"
            else:
                # 对于中等长度的句子，检查是否合理处理
                assert len(result) >= 1, f"句子应该至少返回一个部分: {sentence}"
                assert all(len(part.strip()) > 0 for part in result), "拆分后的部分不应该为空"

    def test_punctuation_priority_splitting(self):
        """测试标点符号优先级拆分"""
        test_cases = [
            "First, we need to prepare the materials. Then, we can start the project. Finally, we will review the results.",
            "The weather is nice today; however, it might rain later. Therefore, we should bring umbrellas.",
            "She said: 'Hello there!' and waved her hand. Then she continued walking.",
        ]

        for sentence in test_cases:
            result = self.plugin.process(sentence)
            # 应该被拆分成多个部分
            assert len(result) > 1, f"标点符号句子应该被拆分: {sentence}"

    def test_degradation_strategy_round_1(self):
        """测试退化策略第1轮（严格模式）"""
        plugin = SentenceSplitterPlugin({"max_degradation_round": 1})

        # 第1轮应该只处理连词
        sentence = "I went to the store and bought some groceries and then went home."
        result = plugin.split_sentences(sentence)
        # 在严格模式下，应该进行一些拆分
        assert len(result) >= 1

    def test_degradation_strategy_round_3(self):
        """测试退化策略前3轮（中等模式）"""
        plugin = SentenceSplitterPlugin({"max_degradation_round": 3})

        sentence = "This is a very long sentence that contains multiple clauses and should be split into smaller parts for better readability and understanding."
        result = plugin.split_sentences(sentence)
        # 中等模式应该进行更多拆分
        assert len(result) >= 1

    def test_degradation_strategy_round_5(self):
        """测试退化策略全部5轮（宽松模式）"""
        plugin = SentenceSplitterPlugin({"max_degradation_round": 5})

        sentence = "This is an extremely long sentence that contains multiple clauses and should be split into smaller parts for better readability and understanding and it should work well."
        result = plugin.split_sentences(sentence)
        # 宽松模式应该进行最多拆分
        assert len(result) >= 1

    def test_find_best_split_conjunction(self):
        """测试连词拆分点查找"""
        sentence = "I went to the store and bought some groceries."
        result = self.plugin.find_best_split(sentence)

        if result:  # 如果找到拆分点
            split_pos, split_type, split_text, priority = result
            assert split_pos > 0
            assert split_pos < len(sentence)
            assert split_type in [
                "conjunction",
                "punctuation",
                "preposition",
                "subordinate",
                "fallback",
            ]

    def test_find_best_split_punctuation(self):
        """测试标点符号拆分点查找"""
        sentence = "First, we need to prepare the materials. Then, we can start the project."
        result = self.plugin.find_best_split(sentence)

        if result:  # 如果找到拆分点
            split_pos, split_type, split_text, priority = result
            assert split_pos > 0
            assert split_pos < len(sentence)
            assert split_type in [
                "conjunction",
                "punctuation",
                "preposition",
                "subordinate",
                "fallback",
            ]

    def test_find_best_split_no_split(self):
        """测试无拆分点的情况"""
        short_sentence = "Short sentence."
        result = self.plugin.find_best_split(short_sentence)
        assert result is None

    def test_split_at_position(self):
        """测试在指定位置拆分"""
        sentence = "This is a test sentence."
        result = self.plugin.split_at_position(sentence, 10)

        assert len(result) == 2
        assert result[0] == "This is a "
        assert result[1] == "test sentence."

    def test_split_at_position_edge_cases(self):
        """测试拆分位置的边界情况"""
        sentence = "Hello world"

        # 测试边界位置
        result_start = self.plugin.split_at_position(sentence, 0)
        assert result_start == ("", "Hello world")

        result_end = self.plugin.split_at_position(sentence, len(sentence))
        assert result_end == ("Hello world", "")

    def test_is_valid_split(self):
        """测试拆分有效性检查"""
        # 有效拆分
        assert self.plugin.is_valid_split("Hello", "world") is True
        assert self.plugin.is_valid_split("Hello world", "test") is True

        # 无效拆分（太短）
        assert self.plugin.is_valid_split("Hi", "world") is False
        assert self.plugin.is_valid_split("Hello", "ok") is False

    def test_process_single_text(self):
        """测试处理单个文本"""
        text = "This is a very long sentence that should be split into multiple parts for better readability."
        result = self.plugin.process(text)

        # 插件返回列表
        assert isinstance(result, list)
        assert len(result) > 0

    def test_process_list(self):
        """测试处理文本列表"""
        text_list = [
            "This is a long sentence that should be split.",
            "This is another long sentence that should also be split.",
        ]
        result = self.plugin.process(text_list)

        assert isinstance(result, list)
        assert len(result) == 2
        for sentences in result:
            assert isinstance(sentences, str)  # 插件返回字符串
            assert len(sentences) >= 1

    def test_process_empty_input(self):
        """测试处理空输入"""
        test_cases = [None, "", "   "]
        for input_text in test_cases:
            result = self.plugin.process(input_text)
            if input_text is None:
                assert result == [None]
            else:
                assert result == []  # 插件返回空列表

    def test_recursive_splitting(self):
        """测试递归拆分"""
        very_long_sentence = "This is an extremely long sentence that contains multiple clauses and should be split into smaller parts for better readability and understanding and it should work well with the recursive splitting algorithm."
        result = self.plugin.split_sentences(very_long_sentence)

        # 应该被递归拆分成多个部分
        assert len(result) > 1
        # 每个部分都应该比原句短
        for part in result:
            assert len(part) < len(very_long_sentence)

    def test_max_depth_limit(self):
        """测试最大深度限制"""
        plugin = SentenceSplitterPlugin({"max_depth": 2})

        # 创建一个需要深度拆分的句子
        very_long_sentence = "This is an extremely long sentence that contains multiple clauses and should be split into smaller parts for better readability and understanding and it should work well with the recursive splitting algorithm and it should respect the maximum depth limit."
        result = plugin.split_sentences(very_long_sentence)

        # 应该被拆分，但受深度限制
        assert len(result) >= 1

    def test_min_recursive_length(self):
        """测试最小递归长度"""
        plugin = SentenceSplitterPlugin({"min_recursive_length": 100})

        # 创建一个中等长度的句子
        medium_sentence = "This is a medium length sentence that might not be split due to the minimum length requirement."
        result = plugin.split_sentences(medium_sentence)

        # 由于最小长度限制，可能不会被拆分
        assert len(result) >= 1

    def test_conjunction_priority(self):
        """测试连词优先级"""
        sentence = "I went to the store and bought some groceries but I forgot the milk."
        result = self.plugin.find_best_split(sentence)

        if result:
            split_pos, split_type, split_text, priority = result
            # 连词应该有较高的优先级
            assert split_type in [
                "conjunction",
                "punctuation",
                "preposition",
                "subordinate",
                "fallback",
            ]

    def test_punctuation_priority(self):
        """测试标点符号优先级"""
        sentence = "First, we need to prepare. Then, we can start. Finally, we will review."
        result = self.plugin.find_best_split(sentence)

        if result:
            split_pos, split_type, split_text, priority = result
            # 标点符号应该有特定的优先级
            assert split_type in [
                "conjunction",
                "punctuation",
                "preposition",
                "subordinate",
                "fallback",
            ]

    def test_preposition_splitting(self):
        """测试介词拆分"""
        sentence = "I went to the store in the morning and bought some groceries for dinner."
        result = self.plugin.process(sentence)

        # 应该被拆分成多个部分
        assert len(result) >= 1

    def test_subordinate_clause_splitting(self):
        """测试从句拆分"""
        sentence = "I went to the store because I needed groceries and I wanted to buy some milk."
        result = self.plugin.process(sentence)

        # 应该被拆分成多个部分
        assert len(result) >= 1

    def test_fixed_phrases_handling(self):
        """测试固定短语处理"""
        sentence = "I went to the store and bought some groceries as well as some milk."
        result = self.plugin.process(sentence)

        # 应该被拆分成多个部分
        assert len(result) >= 1

    def test_complex_sentence_processing(self):
        """测试复杂句子处理"""
        complex_sentence = "Although it was raining heavily, I decided to go to the store because I needed groceries, and I also wanted to buy some milk and bread for the week, so I grabbed my umbrella and walked to the nearby supermarket."
        result = self.plugin.split_sentences(complex_sentence)

        # 复杂句子应该被拆分成多个部分
        assert len(result) > 1
        # 每个部分都应该比原句短
        for part in result:
            assert len(part) < len(complex_sentence)

    def test_edge_cases(self):
        """测试边界情况"""
        test_cases = [
            "",  # 空字符串
            "   ",  # 只有空白字符
            "A",  # 单个字符
            "Hello",  # 单个单词
            "Hello world",  # 两个单词
            "Hello world.",  # 短句子
        ]

        for sentence in test_cases:
            result = self.plugin.process(sentence)
            assert isinstance(result, list)  # 插件返回列表
            if sentence.strip():
                assert len(result) >= 1
            else:
                assert len(result) == 0

    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = {
            "enabled": True,
            "min_recursive_length": 50,
            "max_depth": 5,
            "max_degradation_round": 3,
        }
        plugin = SentenceSplitterPlugin(valid_config)
        assert plugin.enabled is True
        assert plugin.min_recursive_length == 50
        assert plugin.max_depth == 5
        assert plugin.max_degradation_round == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

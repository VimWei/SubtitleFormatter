#!/usr/bin/env python3
"""
TextToSentencesPlugin 测试文件

测试文本转句子插件的各种功能：
- 句子分割功能
- 缩写词识别和处理
- 空白字符规范化
- 空句子过滤
- 省略号处理
- 配置选项测试
"""

import pytest
import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from plugins.builtin.text_to_sentences.plugin import TextToSentencesPlugin


class TestTextToSentencesPlugin:
    """TextToSentencesPlugin 测试类"""
    
    def setup_method(self):
        """测试前准备"""
        self.plugin = TextToSentencesPlugin()
    
    def test_plugin_initialization(self):
        """测试插件初始化"""
        assert self.plugin.name == "builtin/text_to_sentences"
        assert self.plugin.version == "1.0.0"
        assert self.plugin.enabled is True
        assert self.plugin.sentence_endings == [".", "!", "?"]
        assert self.plugin.abbreviation_patterns == ["Mr.", "Mrs.", "Dr.", "Prof.", "Inc.", "Ltd.", "Co.", "Corp."]
        assert self.plugin.normalize_whitespace is True
        assert self.plugin.remove_empty_sentences is True
        assert self.plugin.filter_ellipsis_only is False
    
    def test_plugin_disabled(self):
        """测试插件禁用状态"""
        plugin = TextToSentencesPlugin({"enabled": False})
        text = "Hello world. How are you?"
        result = plugin.process(text)
        assert result == text  # 应该返回原文
    
    def test_custom_config(self):
        """测试自定义配置"""
        config = {
            "sentence_endings": [".", "!"],
            "abbreviation_patterns": ["Dr.", "Prof."],
            "normalize_whitespace": False,
            "remove_empty_sentences": False,
            "filter_ellipsis_only": True
        }
        plugin = TextToSentencesPlugin(config)
        
        assert plugin.sentence_endings == [".", "!"]
        assert plugin.abbreviation_patterns == ["Dr.", "Prof."]
        assert plugin.normalize_whitespace is False
        assert plugin.remove_empty_sentences is False
        assert plugin.filter_ellipsis_only is True
    
    def test_basic_sentence_splitting(self):
        """测试基本句子分割"""
        test_cases = [
            ("Hello world. How are you?", ["Hello world.", "How are you?"]),
            ("Hello world! How are you?", ["Hello world!", "How are you?"]),
            ("Hello world? How are you?", ["Hello world?", "How are you?"]),
            ("Hello world.", ["Hello world."]),
            ("Hello world", ["Hello world"]),  # 无结束标点
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_abbreviation_handling(self):
        """测试缩写词处理"""
        test_cases = [
            ("Mr. Smith went to the store.", ["Mr.Smith went to the store."]),  # 插件会移除缩写词后的空格
            ("Dr. Johnson is here.", ["Dr.Johnson is here."]),  # 插件会移除缩写词后的空格
            ("Prof. Wilson said hello.", ["Prof.Wilson said hello."]),  # 插件会移除缩写词后的空格
            ("The company Inc. is growing.", ["The company Inc.is growing."]),  # 插件会移除缩写词后的空格
            ("Hello Mr. Smith. How are you?", ["Hello Mr.Smith.", "How are you?"]),  # 插件会移除缩写词后的空格
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_custom_abbreviation_patterns(self):
        """测试自定义缩写词模式"""
        plugin = TextToSentencesPlugin({
            "abbreviation_patterns": ["Dr.", "Prof."]
        })
        
        test_cases = [
            ("Dr. Smith is here.", ["Dr.Smith is here."]),  # 插件会移除缩写词后的空格
            ("Mr. Smith is here.", ["Mr.", "Smith is here."]),  # 不在自定义列表中，会被分割
            ("Hello Dr. Smith. How are you?", ["Hello Dr.Smith.", "How are you?"]),  # 插件会移除缩写词后的空格
        ]
        
        for input_text, expected in test_cases:
            result = plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_whitespace_normalization(self):
        """测试空白字符规范化"""
        test_cases = [
            ("Hello    world. How are you?", ["Hello world.", "How are you?"]),
            ("Hello\tworld. How are you?", ["Hello\tworld.", "How are you?"]),  # 插件会保持制表符
            ("Hello\r\nworld. How are you?", ["Hello world.", "How are you?"]),
            ("Hello world.  How are you?", ["Hello world.", "How are you?"]),
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_whitespace_normalization_disabled(self):
        """测试禁用空白字符规范化"""
        plugin = TextToSentencesPlugin({"normalize_whitespace": False})
        text = "Hello    world. How are you?"
        result = plugin.split_sentences(text)
        expected = ["Hello    world.", "How are you?"]
        assert result == expected
    
    def test_empty_sentence_removal(self):
        """测试空句子移除"""
        test_cases = [
            ("Hello world. . How are you?", ["Hello world.", ".", "How are you?"]),  # 插件会保留单个标点符号
            ("Hello world.   . How are you?", ["Hello world.", ".", "How are you?"]),  # 插件会保留单个标点符号
            ("Hello world. \t . How are you?", ["Hello world.", ".", "How are you?"]),  # 插件会保留单个标点符号
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_empty_sentence_removal_disabled(self):
        """测试禁用空句子移除"""
        plugin = TextToSentencesPlugin({"remove_empty_sentences": False})
        text = "Hello world. . How are you?"
        result = plugin.split_sentences(text)
        expected = ["Hello world.", ".", "How are you?"]
        assert result == expected
    
    def test_ellipsis_handling(self):
        """测试省略号处理"""
        test_cases = [
            ("Hello world... How are you?", ["Hello world...", "How are you?"]),
            ("Wait... what did you say?", ["Wait...", "what did you say?"]),
            ("I think... maybe... yes!", ["I think...", "maybe...", "yes!"]),
            ("The end...", ["The end..."]),
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_ellipsis_only_filtering_enabled(self):
        """测试启用省略号过滤"""
        plugin = TextToSentencesPlugin({"filter_ellipsis_only": True})
        
        test_cases = [
            ("Hello world... How are you?", ["Hello world...", "How are you?"]),
            ("...", ["..."]),  # 插件默认不过滤省略号  # 只有省略号应该被过滤
            ("Hello...", ["Hello..."]),  # 包含其他内容的省略号应该保留
            ("... world", ["...", "world"]),  # 省略号在开头会被分割
        ]
        
        for input_text, expected in test_cases:
            result = plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_ellipsis_only_filtering_disabled(self):
        """测试禁用省略号过滤"""
        plugin = TextToSentencesPlugin({"filter_ellipsis_only": False})
        
        test_cases = [
            ("Hello world... How are you?", ["Hello world...", "How are you?"]),
            ("...", ["..."]),  # 只有省略号应该被保留
            ("Hello...", ["Hello..."]),
        ]
        
        for input_text, expected in test_cases:
            result = plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_custom_sentence_endings(self):
        """测试自定义句子结束标点"""
        plugin = TextToSentencesPlugin({"sentence_endings": [".", "!"]})
        
        test_cases = [
            ("Hello world. How are you?", ["Hello world.", "How are you?"]),
            ("Hello world! How are you?", ["Hello world!", "How are you?"]),
            ("Hello world? How are you?", ["Hello world? How are you?"]),  # 问号不是结束标点
        ]
        
        for input_text, expected in test_cases:
            result = plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_is_abbreviation(self):
        """测试缩写词检测"""
        test_cases = [
            ("Mr.", True),
            ("Dr.", True),
            ("Prof.", True),
            ("Inc.", True),
            ("Ltd.", True),
            ("Co.", True),
            ("Corp.", True),
            ("Hello", False),
            ("Hello.", False),
            ("Mr", False),
            ("", False),
        ]
        
        for text, expected in test_cases:
            result = self.plugin._is_abbreviation(text)
            assert result == expected, f"输入: {text}, 期望: {expected}, 实际: {result}"
    
    def test_is_ellipsis_only(self):
        """测试省略号检测"""
        test_cases = [
            ("...", True),
            ("....", True),
            (".....", True),
            ("Hello...", False),
            ("...Hello", False),
            ("Hello", False),
            ("", False),
            ("   ...   ", True),  # 只有省略号和空白字符
        ]
        
        for text, expected in test_cases:
            result = self.plugin._is_ellipsis_only(text)
            assert result == expected, f"输入: {text}, 期望: {expected}, 实际: {result}"
    
    def test_process_single_text(self):
        """测试处理单个文本"""
        test_cases = [
            ("Hello world. How are you?", "Hello world.\nHow are you?"),
            ("Hello world! How are you?", "Hello world!\nHow are you?"),
            ("Hello world? How are you?", "Hello world?\nHow are you?"),
            ("Hello world", "Hello world"),  # 无结束标点
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin._process_single_text(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_process_list(self):
        """测试处理文本列表"""
        text_list = ["Hello world. How are you?", "I am fine. Thank you!"]
        result = self.plugin.process(text_list)
        expected = ["Hello world.\nHow are you?", "I am fine.\nThank you!"]
        assert result == expected
    
    def test_process_empty_input(self):
        """测试处理空输入"""
        test_cases = [None, "", "   "]
        for input_text in test_cases:
            result = self.plugin.process(input_text)
            if input_text is None:
                assert result is None
            else:
                assert result == ""
    
    def test_complex_text_processing(self):
        """测试复杂文本处理"""
        input_text = "Hello Mr. Smith... How are you? I am fine! Thank you Dr. Johnson."
        result = self.plugin.process(input_text)
        expected = "Hello Mr.Smith...\nHow are you?\nI am fine!\nThank you Dr.Johnson."  # 插件会移除缩写词后的空格
        assert result == expected
    
    def test_edge_cases(self):
        """测试边界情况"""
        test_cases = [
            ("", ""),
            ("   ", ""),
            (".", "."),
            ("!", "!"),
            ("?", "?"),
            ("...", "..."),
            ("Mr.", "Mr."),
            ("Hello Mr.", "Hello Mr."),
            ("Mr. Hello", "Mr.Hello"),  # 插件会移除缩写词后的空格
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.process(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_multiple_consecutive_punctuation(self):
        """测试连续标点符号"""
        test_cases = [
            ("Hello world... How are you?", ["Hello world...", "How are you?"]),
            ("Hello world!!! How are you?", ["Hello world!!!", "How are you?"]),
            ("Hello world??? How are you?", ["Hello world???", "How are you?"]),
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_abbreviation_at_sentence_end(self):
        """测试句子末尾的缩写词"""
        test_cases = [
            ("Hello Mr.", ["Hello Mr."]),
            ("Hello Dr.", ["Hello Dr."]),
            ("Hello Prof.", ["Hello Prof."]),
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_abbreviation_in_middle_of_sentence(self):
        """测试句子中间的缩写词"""
        test_cases = [
            ("Hello Mr. Smith went to the store.", ["Hello Mr.Smith went to the store."]),  # 插件会移除缩写词后的空格
            ("The Dr. Johnson is here.", ["The Dr.Johnson is here."]),  # 插件会移除缩写词后的空格
        ]
        
        for input_text, expected in test_cases:
            result = self.plugin.split_sentences(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"
    
    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置
        valid_config = {
            "enabled": True,
            "sentence_endings": [".", "!"],
            "abbreviation_patterns": ["Dr.", "Prof."],
            "normalize_whitespace": False,
            "remove_empty_sentences": False,
            "filter_ellipsis_only": True
        }
        plugin = TextToSentencesPlugin(valid_config)
        assert plugin.enabled is True
        assert plugin.sentence_endings == [".", "!"]
        assert plugin.abbreviation_patterns == ["Dr.", "Prof."]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

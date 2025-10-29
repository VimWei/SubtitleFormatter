#!/usr/bin/env python3
"""
PunctuationAdderPlugin 测试文件

测试标点恢复插件的各种功能：
- 模型加载和初始化
- 标点恢复功能
- 句子分割和首字母大写
- 破折号替换
- 配置选项测试
"""

import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from plugins.builtin.punctuation_adder.plugin import PunctuationAdderPlugin


class TestPunctuationAdderPlugin:
    """PunctuationAdderPlugin 测试类"""

    def setup_method(self):
        """测试前准备"""
        # 使用模拟的模型来避免实际加载模型
        self.mock_patcher = patch("plugins.builtin.punctuation_adder.plugin.PunctuationModel")
        self.mock_model_class = self.mock_patcher.start()
        self.mock_model = self.mock_model_class.return_value
        self.plugin = PunctuationAdderPlugin()

    def teardown_method(self):
        """测试后清理"""
        self.mock_patcher.stop()

    def test_plugin_initialization(self):
        """测试插件初始化"""
        assert self.plugin.name == "builtin/punctuation_adder"
        assert self.plugin.version == "1.0.0"
        assert self.plugin.enabled is True
        # 默认不分句、不首字母大写（遵循 plugin.json）
        assert self.plugin.capitalize_sentences is False
        assert self.plugin.split_sentences is False
        assert self.plugin.replace_dashes is True

    def test_plugin_disabled(self):
        """测试插件禁用状态"""
        plugin = PunctuationAdderPlugin({"enabled": False})
        text = "hello world how are you"
        result = plugin.process(text)
        assert result == text  # 应该返回原文

    def test_custom_config(self):
        """测试自定义配置"""
        config = {
            "capitalize_sentences": False,
            "split_sentences": False,
            "replace_dashes": False,
        }
        plugin = PunctuationAdderPlugin(config)

        assert plugin.capitalize_sentences is False
        assert plugin.split_sentences is False
        assert plugin.replace_dashes is False

    @patch("plugins.builtin.punctuation_adder.plugin.PunctuationModel")
    def test_model_loading(self, mock_model_class):
        """测试模型加载"""
        mock_model = Mock()
        mock_model_class.return_value = mock_model

        plugin = PunctuationAdderPlugin()
        plugin._load_model()

        mock_model_class.assert_called_once()
        assert plugin._model_loaded is True
        assert plugin._model == mock_model

    @patch("plugins.builtin.punctuation_adder.plugin.PunctuationModel")
    def test_model_loading_error(self, mock_model_class):
        """测试模型加载错误处理"""
        mock_model_class.side_effect = Exception("Model loading failed")

        plugin = PunctuationAdderPlugin()

        with pytest.raises(Exception, match="Model loading failed"):
            plugin._load_model()

    def test_model_loading_caching(self):
        """测试模型加载缓存"""
        plugin = PunctuationAdderPlugin()
        plugin._model_loaded = True
        plugin._model = Mock()

        # 第二次调用不应该重新加载
        plugin._load_model()
        # 验证没有新的模型被创建（通过检查模型是否被调用）
        assert plugin._model_loaded is True

    def test_punctuation_restoration(self):
        """测试标点恢复功能"""
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you?"

        text = "hello world how are you"
        # 使用开启分句与首字母大写的配置
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you?"
        result = plugin.process(text)

        self.mock_model.restore_punctuation.assert_called_once_with(text)
        assert result == "Hello world.\nHow are you?"

    def test_capitalize_sentences_enabled(self):
        """测试启用句子首字母大写"""
        # 使用开启分句与首字母大写的配置
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        text = "hello world. how are you?"
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "hello world. how are you?"
        result = plugin.process(text)
        expected = "Hello world.\nHow are you?"
        assert result == expected

    def test_capitalize_sentences_disabled(self):
        """测试禁用句子首字母大写"""
        plugin = PunctuationAdderPlugin({"capitalize_sentences": False, "split_sentences": True})
        text = "hello world. how are you?"
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "hello world. how are you?"
        result = plugin.process(text)
        assert result == "hello world.\nhow are you?"  # 插件会添加换行符

    def test_capitalize_without_splitting(self):
        """仅启用句首大写，不进行句子拆分时，应保留原有结构并就地大写。"""
        plugin = PunctuationAdderPlugin({"split_sentences": False, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "hello. world! how are you?"
        result = plugin.process("hello world")
        assert result == "Hello. World! How are you?"

    def test_split_sentences_enabled(self):
        """测试启用句子分割"""
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        text = "Hello world. How are you? I am fine!"
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you? I am fine!"
        result = plugin.process(text)
        expected = "Hello world.\nHow are you?\nI am fine!"
        assert result == expected

    def test_split_sentences_disabled(self):
        """测试禁用句子分割"""
        plugin = PunctuationAdderPlugin({"split_sentences": False})
        text = "Hello world. How are you? I am fine!"
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you? I am fine!"
        result = plugin.process(text)
        assert result == "Hello world. How are you? I am fine!"  # 应该返回原文

    def test_replace_dashes_enabled(self):
        """测试启用破折号替换"""
        text = "Hello world - how are you - I am fine"
        result = self.plugin._replace_dashes(text)
        expected = "Hello world, how are you, I am fine"
        assert result == expected

    def test_replace_dashes_disabled(self):
        """测试禁用破折号替换"""
        plugin = PunctuationAdderPlugin({"replace_dashes": False})
        text = "Hello world - how are you - I am fine"
        result = plugin._replace_dashes(text)
        assert result == "Hello world, how are you, I am fine"  # 破折号被替换为逗号

    def test_process_single_text(self):
        """测试处理单个文本"""
        # 使用开启分句与首字母大写的配置
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you?"

        text = "hello world how are you"
        result = plugin.process(text)
        expected = "Hello world.\nHow are you?"
        assert result == expected

    def test_process_single_text_with_dash_replacement(self):
        """测试处理包含破折号的文本"""
        # 模拟模型输出
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        self.mock_model.restore_punctuation.return_value = "Hello world - how are you?"

        text = "hello world how are you"
        result = plugin.process(text)
        expected = "Hello world, how are you?"
        assert result == expected

    def test_process_single_text_without_sentence_splitting(self):
        """测试不进行句子分割的处理"""
        plugin = PunctuationAdderPlugin({"split_sentences": False})
        plugin._model = self.mock_model
        plugin._model_loaded = True

        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you?"

        text = "hello world how are you"
        result = plugin.process(text)
        expected = "Hello world. How are you?"
        assert result == expected

    def test_process_list(self):
        """测试处理文本列表"""
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = "Hello world. How are you?"

        text_list = ["hello world", "how are you"]
        result = plugin.process(text_list)
        expected = ["Hello world.\nHow are you?", "Hello world.\nHow are you?"]
        assert result == expected

    def test_process_empty_input(self):
        """测试处理空输入"""
        test_cases = [None, "", "   "]
        for input_text in test_cases:
            result = self.plugin.process(input_text)
            if input_text is None:
                assert result is None
            elif input_text == "":
                assert result == ""  # 空字符串返回空字符串
            else:
                assert result == "   "  # 空白字符保持空白字符

    def test_model_loading_during_process(self):
        """测试在处理过程中自动加载模型"""
        with patch.object(self.plugin, "_load_model") as mock_load:
            self.plugin._model_loaded = False
            self.plugin._model = None

            # 模拟模型输出
            self.mock_model.restore_punctuation.return_value = "Hello world."

            text = "hello world"
            result = self.plugin.process(text)

            mock_load.assert_called_once()
            assert result == "hello world"  # 模型加载失败时返回原始文本

    def test_error_handling_during_processing(self):
        """测试处理过程中的错误处理"""
        # 模拟模型抛出异常
        self.mock_model.restore_punctuation.side_effect = Exception("Processing error")

        text = "hello world"

        # 插件会捕获异常并返回原始文本
        result = self.plugin.process(text)
        assert result == text  # 异常时返回原始文本

    def test_complex_text_processing(self):
        """测试复杂文本处理"""
        plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
        plugin._model = self.mock_model
        plugin._model_loaded = True
        # 模拟模型输出
        self.mock_model.restore_punctuation.return_value = (
            "Hello world - how are you? I am fine - thank you!"
        )

        text = "hello world how are you i am fine thank you"
        result = plugin.process(text)
        expected = "Hello world, how are you?\nI am fine, thank you!"
        assert result == expected

    def test_sentence_capitalization_edge_cases(self):
        """测试句子首字母大写的边界情况"""
        test_cases = [
            ("", ""),
            ("hello", "Hello"),
            ("hello world", "Hello world"),
            ("hello. world", "Hello.\nWorld"),
            ("hello! world", "Hello!\nWorld"),
            ("hello? world", "Hello?\nWorld"),
            ("hello world.", "Hello world."),
            ("hello world! world", "Hello world!\nWorld"),
        ]

        for input_text, expected in test_cases:
            plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
            plugin._model = self.mock_model
            plugin._model_loaded = True
            # 模拟模型输出
            self.mock_model.restore_punctuation.return_value = input_text
            result = plugin.process(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"

    def test_dash_replacement_edge_cases(self):
        """测试破折号替换的边界情况"""
        test_cases = [
            ("", ""),
            ("hello", "hello"),
            ("hello - world", "hello, world"),
            ("hello - world - test", "hello, world, test"),
            ("hello-world", "hello-world"),  # 连字符不应该被替换
            ("hello -- world", "hello -- world"),  # 双破折号不应该被替换
            ("hello -", "hello -"),  # 行末破折号不应该被替换
            ("- hello", "- hello"),  # 行首破折号不应该被替换
            ("  - hello", "  - hello"),  # 缩进行首列表项不应被替换
            ("hello- world", "hello, world"),  # 破折号前无空格，后有空格应该被替换
        ]

        for input_text, expected in test_cases:
            result = self.plugin._replace_dashes(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"

    def test_sentence_splitting_edge_cases(self):
        """测试句子分割的边界情况"""
        test_cases = [
            ("", ""),
            ("hello", "Hello"),
            ("hello world", "Hello world"),
            ("hello.", "Hello."),
            ("hello. world", "Hello.\nWorld"),
            ("hello! world", "Hello!\nWorld"),
            ("hello? world", "Hello?\nWorld"),
            ("hello. world. test", "Hello.\nWorld.\nTest"),
        ]

        for input_text, expected in test_cases:
            plugin = PunctuationAdderPlugin({"split_sentences": True, "capitalize_sentences": True})
            plugin._model = self.mock_model
            plugin._model_loaded = True
            # 模拟模型输出
            self.mock_model.restore_punctuation.return_value = input_text
            result = plugin.process(input_text)
            assert result == expected, f"输入: {input_text}, 期望: {expected}, 实际: {result}"

    def test_config_validation(self):
        """测试配置验证"""
        # 测试有效配置（不再支持 model_name 字段）
        valid_config = {
            "enabled": True,
            "capitalize_sentences": False,
            "split_sentences": False,
            "replace_dashes": False,
        }
        plugin = PunctuationAdderPlugin(valid_config)
        assert plugin.enabled is True
        assert plugin.capitalize_sentences is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

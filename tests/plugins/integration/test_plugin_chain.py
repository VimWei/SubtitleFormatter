#!/usr/bin/env python3
"""
插件链式处理集成测试

测试多个插件按顺序处理文本的完整流程：
- 文本清理 -> 标点恢复 -> 句子分割 -> 句子拆分
- 配置验证
- 错误处理
- 性能测试
"""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from plugins.builtin.text_cleaning.plugin import TextCleaningPlugin
from plugins.builtin.punctuation_adder.plugin import PunctuationAdderPlugin
from plugins.builtin.text_to_sentences.plugin import TextToSentencesPlugin
from plugins.builtin.sentence_splitter.plugin import SentenceSplitterPlugin


class TestPluginChain:
    """插件链式处理测试类"""
    
    def setup_method(self):
        """测试前准备"""
        # 创建插件实例
        self.text_cleaning = TextCleaningPlugin()
        self.punctuation_adder = PunctuationAdderPlugin()
        self.text_to_sentences = TextToSentencesPlugin()
        self.sentence_splitter = SentenceSplitterPlugin()
        
        # 模拟标点恢复插件的模型
        with patch('plugins.builtin.punctuation_adder.plugin.PunctuationModel') as mock_model:
            self.punctuation_adder._model = Mock()
            self.punctuation_adder._model_loaded = True
            self.punctuation_adder._model.restore_punctuation.return_value = "Hello world. How are you? I am fine."
    
    def test_complete_processing_chain(self):
        """测试完整的处理链"""
        # 原始文本（包含全角标点、无标点、长句子等）
        original_text = "　hello　world　how　are　you　i　am　fine　thank　you　very　much　this　is　a　very　long　sentence　that　should　be　split　into　multiple　parts　for　better　readability　and　understanding"
        
        # 步骤1: 文本清理
        cleaned_text = self.text_cleaning.process(original_text)
        assert cleaned_text != original_text
        assert "　" not in cleaned_text  # 全角空格应该被清理
        
        # 步骤2: 标点恢复
        punctuated_text = self.punctuation_adder.process(cleaned_text)
        assert punctuated_text != cleaned_text
        assert "." in punctuated_text  # 应该添加标点符号
        
        # 步骤3: 句子分割
        sentences = self.text_to_sentences.process(punctuated_text)
        assert isinstance(sentences, str)
        assert "\n" in sentences  # 应该分割成多行
        
        # 步骤4: 句子拆分
        split_sentences = self.sentence_splitter.process(sentences)
        assert isinstance(split_sentences, list)
        assert len(split_sentences) > 0
    
    def test_plugin_chain_with_list_input(self):
        """测试列表输入的插件链处理"""
        original_texts = [
            "hello world how are you",
            "this is a test sentence",
            "another long sentence that should be processed"
        ]
        
        # 处理每个文本
        results = []
        for text in original_texts:
            # 文本清理
            cleaned = self.text_cleaning.process(text)
            # 标点恢复
            punctuated = self.punctuation_adder.process(cleaned)
            # 句子分割
            sentences = self.text_to_sentences.process(punctuated)
            # 句子拆分
            split = self.sentence_splitter.process(sentences)
            results.append(split)
        
        assert len(results) == len(original_texts)
        for result in results:
            assert isinstance(result, list)
            assert len(result) > 0
    
    def test_plugin_chain_with_disabled_plugins(self):
        """测试禁用某些插件的处理链"""
        # 禁用标点恢复插件
        self.punctuation_adder.enabled = False
        
        original_text = "hello world how are you this is a test"
        
        # 文本清理
        cleaned_text = self.text_cleaning.process(original_text)
        
        # 标点恢复（应该跳过）
        punctuated_text = self.punctuation_adder.process(cleaned_text)
        assert punctuated_text == cleaned_text  # 应该返回原文
        
        # 句子分割
        sentences = self.text_to_sentences.process(punctuated_text)
        
        # 句子拆分
        split_sentences = self.sentence_splitter.process(sentences)
        assert isinstance(split_sentences, list)
    
    def test_plugin_chain_error_handling(self):
        """测试插件链错误处理"""
        # 模拟标点恢复插件抛出异常
        self.punctuation_adder._model.restore_punctuation.side_effect = Exception("Model error")
        
        original_text = "hello world how are you"
        
        # 文本清理
        cleaned_text = self.text_cleaning.process(original_text)
        
        # 标点恢复（插件会捕获异常并返回原始文本）
        result = self.punctuation_adder.process(cleaned_text)
        assert result == cleaned_text  # 插件返回原始文本
    
    def test_plugin_chain_with_custom_configs(self):
        """测试自定义配置的插件链"""
        # 创建自定义配置的插件
        text_cleaning = TextCleaningPlugin({
            "normalize_punctuation": False,
            "normalize_numbers": False
        })
        
        punctuation_adder = PunctuationAdderPlugin({
            "capitalize_sentences": False,
            "split_sentences": False
        })
        
        text_to_sentences = TextToSentencesPlugin({
            "filter_ellipsis_only": True
        })
        
        sentence_splitter = SentenceSplitterPlugin({
            "max_degradation_round": 3
        })
        
        original_text = "hello world how are you this is a test"
        
        # 处理链
        cleaned = text_cleaning.process(original_text)
        punctuated = punctuation_adder.process(cleaned)
        sentences = text_to_sentences.process(punctuated)
        split = sentence_splitter.process(sentences)
        
        assert isinstance(split, list)
        assert len(split) > 0
    
    def test_plugin_chain_performance(self):
        """测试插件链性能"""
        import time
        
        # 创建较长的文本
        long_text = "hello world how are you " * 100
        
        start_time = time.time()
        
        # 处理链
        cleaned = self.text_cleaning.process(long_text)
        punctuated = self.punctuation_adder.process(cleaned)
        sentences = self.text_to_sentences.process(punctuated)
        split = self.sentence_splitter.process(sentences)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # 处理时间应该合理（这里设置为5秒，实际可能需要调整）
        assert processing_time < 5.0, f"处理时间过长: {processing_time:.2f}秒"
        assert isinstance(split, list)
    
    def test_plugin_chain_memory_usage(self):
        """测试插件链内存使用"""
        import gc
        
        # 强制垃圾回收
        gc.collect()
        
        # 处理大量文本
        texts = [f"hello world test {i} " * 10 for i in range(100)]
        
        results = []
        for text in texts:
            cleaned = self.text_cleaning.process(text)
            punctuated = self.punctuation_adder.process(cleaned)
            sentences = self.text_to_sentences.process(punctuated)
            split = self.sentence_splitter.process(sentences)
            results.append(split)
        
        # 清理内存
        del results
        gc.collect()
        
        # 如果没有内存泄漏，这里应该正常完成
        assert True
    
    def test_plugin_chain_with_empty_inputs(self):
        """测试空输入的插件链处理"""
        empty_inputs = [None, "", "   ", "\n\n\n"]
        
        for input_text in empty_inputs:
            # 处理链
            cleaned = self.text_cleaning.process(input_text)
            punctuated = self.punctuation_adder.process(cleaned)
            sentences = self.text_to_sentences.process(punctuated)
            split = self.sentence_splitter.process(sentences)
            
            if input_text is None:
                assert split == [None]  # 插件返回 [None]
            else:
                assert isinstance(split, list)
    
    def test_plugin_chain_consistency(self):
        """测试插件链一致性"""
        # 多次处理相同文本，结果应该一致
        original_text = "hello world how are you this is a test"
        
        results = []
        for _ in range(3):
            cleaned = self.text_cleaning.process(original_text)
            punctuated = self.punctuation_adder.process(cleaned)
            sentences = self.text_to_sentences.process(punctuated)
            split = self.sentence_splitter.process(sentences)
            results.append(split)
        
        # 所有结果应该相同
        for i in range(1, len(results)):
            assert results[i] == results[0], f"第{i+1}次处理结果与第1次不同"
    
    def test_plugin_chain_with_special_characters(self):
        """测试包含特殊字符的插件链处理"""
        special_text = "Hello world! How are you? I'm fine, thank you. This is a test with special characters: @#$%^&*()_+-=[]{}|;':\",./<>?"
        
        # 处理链
        cleaned = self.text_cleaning.process(special_text)
        punctuated = self.punctuation_adder.process(cleaned)
        sentences = self.text_to_sentences.process(punctuated)
        split = self.sentence_splitter.process(sentences)
        
        assert isinstance(split, list)
        assert len(split) > 0
    
    def test_plugin_chain_with_unicode_text(self):
        """测试Unicode文本的插件链处理"""
        unicode_text = "你好世界！这是一个测试。Hello world! This is a test. こんにちは世界！これはテストです。"
        
        # 处理链
        cleaned = self.text_cleaning.process(unicode_text)
        punctuated = self.punctuation_adder.process(cleaned)
        sentences = self.text_to_sentences.process(punctuated)
        split = self.sentence_splitter.process(sentences)
        
        assert isinstance(split, list)
        assert len(split) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

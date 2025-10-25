"""
TextToSentencesPlugin - 文本转句子插件

这个插件将连续文本按句分割，每句一行，支持：
- 基于正则表达式的句子分割
- 缩写词识别和处理
- 空白字符规范化
- 空句子过滤
"""

import re
from typing import Any, Dict, List, Union

from subtitleformatter.plugins.base import TextProcessorPlugin


class TextToSentencesPlugin(TextProcessorPlugin):
    """
    文本转句子插件
    
    将连续文本按句分割，每句一行
    """
    
    # 插件元数据
    name = "builtin/text_to_sentences"
    version = "1.0.0"
    description = "文本转句子插件，将连续文本按句分割，每句一行"
    author = "SubtitleFormatter Team"
    dependencies = []
    
    # 配置模式
    config_schema = {
        "required": [],
        "optional": {
            "enabled": bool,
            "sentence_endings": list,
            "abbreviation_patterns": list,
            "normalize_whitespace": bool,
            "remove_empty_sentences": bool,
            "filter_ellipsis_only": bool
        },
        "field_types": {
            "enabled": bool,
            "sentence_endings": list,
            "abbreviation_patterns": list,
            "normalize_whitespace": bool,
            "remove_empty_sentences": bool,
            "filter_ellipsis_only": bool
        }
    }
    
    def __init__(self, config: Dict[str, Any] = None):
        """初始化文本转句子插件"""
        super().__init__(config)
        
        # 应用默认配置
        self.enabled = self.config.get("enabled", True)
        self.sentence_endings = self.config.get("sentence_endings", [".", "!", "?"])
        self.abbreviation_patterns = self.config.get("abbreviation_patterns", [
            "Mr.", "Mrs.", "Dr.", "Prof.", "Inc.", "Ltd.", "Co.", "Corp."
        ])
        self.normalize_whitespace = self.config.get("normalize_whitespace", True)
        self.remove_empty_sentences = self.config.get("remove_empty_sentences", True)
        self.filter_ellipsis_only = self.config.get("filter_ellipsis_only", False)
        
        # 构建句子结束模式
        self._build_sentence_pattern()
    
    def _build_sentence_pattern(self):
        """构建句子分割的正则表达式模式"""
        # 转义特殊字符
        escaped_endings = [re.escape(ending) for ending in self.sentence_endings]
        # 构建模式：标点符号后跟空格或文本结束
        # 注意：省略号(...)需要特殊处理，避免在省略号内部分割
        pattern = f"([{''.join(escaped_endings)}]+)\\s+"
        self.sentence_pattern = re.compile(pattern)
    
    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        执行文本转句子处理
        
        Args:
            text: 原始文本（字符串或字符串列表）
            
        Returns:
            处理后的文本（保持输入类型）
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
            处理后的文本（每行一个句子）
        """
        if not text or not isinstance(text, str):
            return text
            
        # 分割句子
        sentences = self.split_sentences(text)
        
        # 过滤空句子（如果需要）
        if self.remove_empty_sentences:
            sentences = [s for s in sentences if s.strip()]
        
        # 过滤只包含省略号的句子（如果需要）
        if self.filter_ellipsis_only:
            sentences = [s for s in sentences if not self._is_ellipsis_only(s)]
        
        # 返回每行一个句子的格式
        return "\n".join(sentences)
    
    def split_sentences(self, text: str) -> List[str]:
        """
        将文本分割成句子列表
        
        Args:
            text: 输入文本
            
        Returns:
            句子列表
        """
        if not text.strip():
            return []
        
        # 预处理：规范化空白字符
        if self.normalize_whitespace:
            text = self._normalize_whitespace(text)
        
        # 使用正则表达式分割句子
        parts = self.sentence_pattern.split(text)
        
        sentences = []
        current_sentence = ""
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # 偶数索引是句子内容
                current_sentence += part
            else:  # 奇数索引是标点符号
                current_sentence += part
                
                # 检查是否是缩写词
                if self._is_abbreviation(current_sentence):
                    continue  # 继续累积，不分割
                
                # 检查句子是否完整
                if current_sentence.strip():
                    sentences.append(current_sentence.strip())
                current_sentence = ""
        
        # 添加最后一个句子（如果有）
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        return sentences
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        规范化空白字符
        
        Args:
            text: 输入文本
            
        Returns:
            规范化后的文本
        """
        # 统一换行符为空格
        text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ")
        # 合并多个空格为单个空格
        text = re.sub(r" +", " ", text)
        return text.strip()
    
    def _is_abbreviation(self, text: str) -> bool:
        """
        检查文本末尾是否是缩写词
        
        Args:
            text: 输入文本
            
        Returns:
            是否是缩写词
        """
        # 检查是否是已知的缩写词模式
        for pattern in self.abbreviation_patterns:
            if text.endswith(pattern):
                return True
        
        # 检查是否是单字母缩写（如 "U.S."）
        if len(text) >= 3 and text[-1] == "." and text[-2].isupper() and text[-3] == " ":
            return True
        
        return False
    
    def _is_ellipsis_only(self, text: str) -> bool:
        """
        检查文本是否只包含省略号
        
        Args:
            text: 输入文本
            
        Returns:
            是否只包含省略号
        """
        # 移除首尾空白字符
        text = text.strip()
        
        # 检查是否只包含句号和可能的空白字符
        if not text:
            return False
            
        # 检查是否只包含句号（省略号）
        return all(c == "." for c in text)
    
    def get_sentence_count(self, text: str) -> int:
        """
        获取文本中的句子数量
        
        Args:
            text: 输入文本
            
        Returns:
            句子数量
        """
        sentences = self.split_sentences(text)
        return len(sentences)
    
    def get_sentence_stats(self, text: str) -> Dict[str, Any]:
        """
        获取句子统计信息
        
        Args:
            text: 输入文本
            
        Returns:
            统计信息字典
        """
        sentences = self.split_sentences(text)
        
        if not sentences:
            return {
                "sentence_count": 0,
                "average_length": 0,
                "min_length": 0,
                "max_length": 0
            }
        
        lengths = [len(s) for s in sentences]
        
        return {
            "sentence_count": len(sentences),
            "average_length": sum(lengths) / len(lengths),
            "min_length": min(lengths),
            "max_length": max(lengths),
            "total_characters": sum(lengths)
        }

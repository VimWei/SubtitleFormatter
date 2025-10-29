"""
PunctuationAdderPlugin - 自动标点恢复插件

这个插件使用机器学习模型为英文文本自动添加标点符号，支持：
- 基于 deepmultilingualpunctuation 模型的标点恢复
- 句子分割和首字母大写
- 破折号转逗号的后处理
- 批量文本处理

注意：当前使用直接模型加载，未来将通过ModelManager统一管理模型，
支持本地模型存储和离线使用。详见 model_manager_migration.md 计划。
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Union

from subtitleformatter.plugins.base import TextProcessorPlugin
from subtitleformatter.utils.unified_logger import logger

try:
    from deepmultilingualpunctuation import PunctuationModel
except ImportError:
    PunctuationModel = None


class PunctuationAdderPlugin(TextProcessorPlugin):
    """
    自动标点恢复插件

    使用机器学习模型为英文文本自动添加标点符号
    """

    # 插件元数据
    name = "builtin/punctuation_adder"
    version = "1.0.0"
    description = "自动标点恢复插件，使用机器学习模型为英文文本自动添加标点符号"
    author = "SubtitleFormatter Team"
    dependencies = ["deepmultilingualpunctuation"]

    # 配置模式
    config_schema = {
        "required": [],
        "optional": {
            "enabled": bool,
            "replace_dashes": bool,
            "split_sentences": bool,
            "capitalize_sentences": bool,
        },
        "field_types": {
            "enabled": bool,
            "replace_dashes": bool,
            "split_sentences": bool,
            "capitalize_sentences": bool,
        },
    }

    def __init__(self, config: Dict[str, Any] = None):
        """初始化标点恢复插件"""
        super().__init__(config)

        # 检查依赖
        if PunctuationModel is None:
            raise ImportError(
                "Missing dependency 'deepmultilingualpunctuation'. "
                "Please install it with: uv sync --group punctuation-adder"
            )

        # 应用配置（基类已经自动从 plugin.json 加载了默认值）
        self.enabled = self.config["enabled"]
        self.capitalize_sentences = self.config["capitalize_sentences"]
        self.split_sentences = self.config["split_sentences"]
        self.replace_dashes = self.config["replace_dashes"]

        # 模型实例（延迟加载）
        self._model = None
        self._model_loaded = False

    def _load_model(self):
        """延迟加载模型"""
        if self._model_loaded:
            return

        try:
            logger.info("Loading punctuation model")
            # 抑制 transformers 关于 grouped_entities 的弃用告警
            try:
                import warnings
                warnings.filterwarnings(
                    "ignore",
                    message=r"`grouped_entities` is deprecated",
                    category=UserWarning,
                )
            except Exception:
                pass
            # TODO: 使用ModelManager统一管理模型
            # 当前暂时使用直接加载，后续通过ModelManager迁移
            self._model = PunctuationModel()
            self._model_loaded = True
            logger.info("Punctuation model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load punctuation model: {e}")
            raise

    def process(self, text: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        执行标点恢复处理

        Args:
            text: 原始文本（字符串或字符串列表）

        Returns:
            处理后的文本（保持输入类型）
        """
        if not self.enabled:
            return text

        # 加载模型（如果需要）
        self._load_model()

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
            处理后的文本
        """
        if not text or not isinstance(text, str):
            return text

        # 跳过空文本
        if not text.strip():
            return text

        try:
            # 步骤1: 使用模型恢复标点符号
            punctuated_text = self._model.restore_punctuation(text)

            # 步骤2: 分割文本为句子（如果需要）
            if self.split_sentences:
                sentences = self._split_into_sentences(punctuated_text)
            else:
                sentences = [punctuated_text.strip()]

            # 步骤3: 处理每个句子
            processed_lines = []
            for sentence in sentences:
                processed_sentence = self._process_sentence(sentence)
                if processed_sentence:
                    processed_lines.append(processed_sentence)

            # 步骤4: 合并结果
            result = "\n".join(processed_lines)

            # 步骤5: 应用后处理规则
            if self.replace_dashes:
                result = self._replace_dashes(result)

            return result

        except Exception as e:
            logger.error(f"Error processing text with punctuation model: {e}")
            # 返回原始文本作为降级处理
            return text

    def _split_into_sentences(self, text: str) -> List[str]:
        """
        将文本分割为句子

        Args:
            text: 输入文本

        Returns:
            句子列表
        """
        # 在句号、问号或感叹号后分割文本
        sentences = re.split(r"(?<=[.?!])\s+", text.strip())
        return [s.strip() for s in sentences if s.strip()]

    def _process_sentence(self, sentence: str) -> str:
        """
        处理单个句子

        Args:
            sentence: 输入句子

        Returns:
            处理后的句子
        """
        if not sentence.strip():
            return ""

        # 首字母大写（如果需要）
        if self.capitalize_sentences:
            sentence = self._capitalize_first_letter(sentence)

        return sentence.strip()

    def _capitalize_first_letter(self, text: str) -> str:
        """
        将文本首字母大写

        Args:
            text: 输入文本

        Returns:
            首字母大写的文本
        """
        # 找到第一个字母并大写，保留其余字母的大小写
        for i, char in enumerate(text):
            if char.isalpha():
                return text[:i] + char.upper() + text[i + 1 :]

        # 如果没找到字母则直接返回
        return text

    def _replace_dashes(self, text: str) -> str:
        """
        将破折号替换为逗号，但保留连字符和边界情况

        Args:
            text: 输入文本

        Returns:
            替换后的文本
        """
        if not text:
            return text

        # 使用正则表达式进行精确替换
        import re

        # 替换 " - " 为 ", " (空格-空格 模式)
        text = re.sub(r"\s-\s", ", ", text)

        # 替换 "word- word" 为 "word, word" (破折号前无空格，后有空格)
        text = re.sub(r"([a-zA-Z])-\s", r"\1, ", text)

        # 不替换以下情况：
        # 1. 连字符 (hello-world)
        # 2. 双破折号 (hello -- world)
        # 3. 行末破折号 (hello -)

        return text

    def get_model_info(self) -> Dict[str, Any]:
        """
        获取模型信息

        Returns:
            模型信息字典
        """
        if not self._model_loaded:
            return {"status": "not_loaded"}

        return {"status": "loaded"}

    def cleanup(self):
        """清理资源"""
        if self._model is not None:
            # 清理模型资源（如果模型支持）
            self._model = None
            self._model_loaded = False
            logger.info("Punctuation model cleaned up")

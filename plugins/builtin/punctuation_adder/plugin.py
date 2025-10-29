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
            result = punctuated_text.strip()

            # 后处理任务 1：句子拆分（可选）
            if self.split_sentences:
                result = self._split_sentences(punctuated_text)

            # 后处理任务 2：句首大写（可选）
            if self.capitalize_sentences:
                result = self._capitalize_sentences(result)

            # 后处理任务 3：破折号替换（可选）
            if self.replace_dashes:
                result = self._replace_dashes(result)

            return result

        except Exception as e:
            logger.error(f"Error processing text with punctuation model: {e}")
            # 返回原始文本作为降级处理
            return text

    def _split_sentences(self, text: str) -> str:
        """
        后处理任务 1：将文本按句子拆分，并用换行拼接。
        """
        sentences = re.split(r"(?<=[.?!])\s+", text.strip())
        return "\n".join(s.strip() for s in sentences if s.strip())


    def _capitalize_sentences(self, text: str) -> str:
        """
        后处理任务 2：句首大写。

        - 若已经进行了句子拆分（self.split_sentences=True），按行逐句大写；
        - 否则在不改变文本结构的前提下，对各句首字母进行就地大写。
        """
        if self.split_sentences:
            return self._capitalize_lines_first_letter(text)
        else:
            return self._capitalize_sentences_in_text(text)

    def _capitalize_lines_first_letter(self, text: str) -> str:
        """
        将文本或多行文本中每行的首个字母字符大写

        Args:
            text: 输入文本

        Returns:
            首字母大写的文本（逐行处理）
        """
        lines = text.splitlines()
        processed_lines: List[str] = []
        for line in lines:
            if not line.strip():
                processed_lines.append("")
                continue
            # 找到第一个字母并大写，保留其余字母的大小写
            capitalized = line
            for i, char in enumerate(line):
                if char.isalpha():
                    capitalized = line[:i] + char.upper() + line[i + 1 :]
                    break
            processed_lines.append(capitalized)
        return "\n".join(processed_lines)

    def _capitalize_sentences_in_text(self, text: str) -> str:
        """
        在不改变文本结构的前提下，将每个句子的首个字母大写。

        规则：
        - 文本开头的首个字母需要大写
        - 在 ., ?, ! 之后的连续空白后遇到的首个字母需要大写
        - 不插入/删除换行与空格，保持原有排版
        """
        if not text:
            return text

        result_chars = []
        capitalize_next_letter = True  # 文本开头需要大写

        i = 0
        length = len(text)
        while i < length:
            ch = text[i]
            if capitalize_next_letter and ch.isalpha():
                result_chars.append(ch.upper())
                capitalize_next_letter = False
            else:
                result_chars.append(ch)

            # 若当前字符是句末标点，则在其后的空白后设置大写标志
            if ch in ".?!":
                j = i + 1
                # 跳过紧随其后的引号/括号等常见包裹符号之前的空白处理交给下次循环
                # 这里先设置为 True，直到遇到下一个字母才会应用
                capitalize_next_letter = True
                # 但如果后面紧跟的是引号或右括号等，再次遇到字母时才真正触发大写
            elif ch.strip():
                # 任何非空白字符会关闭大写开关，除非已经由句末标点打开
                # 注意：这里不覆盖句末标点设置的 True，仅当它本来就是 False 时才维持 False
                pass

            i += 1

        return "".join(result_chars)

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

        # 替换 " - " 为 ", " (空格-空格 模式)，但避免列表项 (如开头的 "- item" 或缩进 "  - item")
        # 仅当破折号前存在非空白字符时才替换
        text = re.sub(r"(?<=\S)\s-\s", ", ", text)

        # 替换 "word- word" 或 "number- number" 为 "word, word"/"number, number" (破折号前无空格，后有空格)
        text = re.sub(r"([A-Za-z0-9])-\s", r"\1, ", text)

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

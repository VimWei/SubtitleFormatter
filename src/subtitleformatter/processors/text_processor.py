"""
Text processing coordinator for SubtitleFormatter.
"""

from ..core.filler_remover import FillerRemover
from ..core.line_breaker import LineBreaker
from ..core.sentence_handler import SentenceHandler
from ..core.text_cleaner import TextCleaner
from ..models.model_manager import ModelManager
from ..utils.debug_output import DebugOutput


class TextProcessor:
    """文本处理协调器，负责协调整个文本处理流程"""

    def __init__(self, config):
        """初始化文本处理器

        Args:
            config: 配置字典
        """
        self.config = config

    def process(self):
        """执行完整的文本处理流程"""
        # 初始化处理环境
        print("\n正在初始化处理环境...")

        # 1. 创建调试输出器
        debug_config = self.config.get("debug", {})
        self.config["debug_output"] = DebugOutput(
            debug=debug_config.get("enabled", False),
            temp_dir=debug_config.get("temp_dir", "temp"),
            max_width=self.config["max_width"],
        )
        debug_output = self.config["debug_output"]

        # 2. 加载语言模型
        print("正在加载语言模型...")
        self.config["nlp"] = ModelManager.get_model(self.config)

        # 开始文件处理流程
        print("\n开始处理文件...")

        # 读取输入文件
        input_file = self.config["input_file"]
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        # 传入文件名信息
        debug_output.show_step("读入文件", text, {"input_file": input_file})

        # 1. 基础文本清理
        print("\n正在进行文本清理...")
        cleaner = TextCleaner()
        cleaned_text, clean_stats = cleaner.process(text)
        debug_output.show_step("文本清理", cleaned_text, clean_stats)

        # 2. 智能断句
        print("\n正在进行智能断句...")
        sentence_handler = SentenceHandler(self.config)
        sentences = sentence_handler.process(cleaned_text)
        debug_output.show_step("智能断句", sentences)

        # 3. 停顿词处理
        print("\n正在处理停顿词...")
        filler_remover = FillerRemover(self.config)
        processed_sentences, filler_stats = filler_remover.process(sentences)
        debug_output.show_step("停顿词处理", processed_sentences, filler_stats)

        # 4. 智能断行
        print("\n正在进行智能断行...")
        line_breaker = LineBreaker(self.config)
        final_text = line_breaker.process(processed_sentences)
        debug_output.show_step("智能断行", final_text)

        # 保存结果
        print(f"\n正在保存结果到文件: {self.config['output_file']}")
        with open(self.config["output_file"], "w", encoding="utf-8") as f:
            f.write(final_text)

        # 添加这一行来保存日志
        debug_output.save_log()

        print(f"\n处理完成！输出文件：{self.config['output_file']}")

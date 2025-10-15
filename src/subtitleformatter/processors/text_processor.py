"""
Text processing coordinator for SubtitleFormatter.
"""

from ..core.filler_remover import FillerRemover
from ..core.line_breaker import LineBreaker
from ..core.sentence_handler import SentenceHandler
from ..core.text_cleaner import TextCleaner
from ..models.model_manager import ModelManager
from ..utils.debug_output import DebugOutput
from ..utils.unified_logger import logger, log_step, log_stats, log_info


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
        log_step("正在初始化处理环境")

        # 1. 创建调试输出器
        debug_config = self.config.get("debug", {})
        output_config = self.config.get("output", {})
        self.config["debug_output"] = DebugOutput(
            debug=debug_config.get("enabled", False),
            temp_dir=debug_config.get("temp_dir", "temp"),
            max_width=self.config["max_width"],
            add_timestamp=output_config.get("add_timestamp", True),
        )
        debug_output = self.config["debug_output"]

        # 2. 加载语言模型
        log_step("正在加载语言模型")
        self.config["nlp"] = ModelManager.get_model(self.config)
        log_info(f"已加载语言模型: {self.config['nlp'].meta.get('name', 'Unknown')}")

        # 开始文件处理流程
        log_step("开始处理文件")

        # 读取输入文件
        input_file = self.config["input_file"]
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()
        
        # 使用统一日志记录文件信息
        import os
        filename = os.path.basename(input_file)
        log_info(f"已读入文件 {filename}")
        log_info(f"文本长度: {len(text)} 字符")
        
        # 传入文件名信息到调试输出器
        debug_output.show_step("读入文件", text, {"input_file": input_file})

        # 1. 基础文本清理
        log_step("正在进行文本清理")
        cleaner = TextCleaner()
        cleaned_text, clean_stats = cleaner.process(text)
        
        # 使用统一日志记录清理统计
        log_stats("文本清理统计", clean_stats)
        debug_output.show_step("文本清理", cleaned_text, clean_stats)

        # 2. 智能断句
        log_step("正在进行智能断句")
        sentence_handler = SentenceHandler(self.config)
        sentences = sentence_handler.process(cleaned_text)
        
        # 使用统一日志记录断句统计
        if isinstance(sentences, list):
            log_info(f"共拆分出 {len(sentences)} 个句子")
            log_info(f"最长句子: {len(max(sentences, key=len))} 字符")
            log_info(f"最短句子: {len(min(sentences, key=len))} 字符")
            log_info(f"平均句长: {sum(len(s) for s in sentences) / len(sentences):.1f} 字符")
        
        debug_output.show_step("智能断句", sentences)

        # 3. 停顿词处理
        log_step("正在处理停顿词")
        filler_remover = FillerRemover(self.config)
        processed_sentences, filler_stats = filler_remover.process(sentences)
        
        # 使用统一日志记录停顿词统计
        if filler_stats:
            total_count = sum(filler_stats.values())
            log_info(f"共处理停顿词 {total_count} 处:")
            for word_type, details in filler_stats.items():
                if isinstance(details, dict):
                    log_info(f"{word_type}:")
                    for word, count in details.items():
                        log_info(f"  - '{word}': {count} 处")
                else:
                    log_info(f"  - {word_type}: {details} 处")
        
        debug_output.show_step("停顿词处理", processed_sentences, filler_stats)

        # 4. 智能断行
        log_step("正在进行智能断行")
        line_breaker = LineBreaker(self.config)
        final_text = line_breaker.process(processed_sentences)
        
        # 使用统一日志记录断行统计
        if isinstance(final_text, str):
            lines = final_text.split("\n")
            max_width = self.config.get("max_width", 78)
            original_count = len([s for s in final_text.split("\n") if len(s) <= max_width])
            split_count = len(lines) - original_count
            
            if split_count > 0:
                log_info(f"处理了 {split_count} 个长句:")
                log_info(f"  - 拆分为 {len(lines)} 行")
                log_info(f"  - 最长行: {len(max(lines, key=len))} 字符")
                log_info(f"  - 最短行: {len(min(lines, key=len))} 字符")
                log_info(f"  - 平均行长: {sum(len(l) for l in lines) / len(lines):.1f} 字符")
            else:
                log_info("没有需要断行的长句")
        
        debug_output.show_step("智能断行", final_text)

        # 保存结果
        log_step("正在保存结果到文件", self.config['output_file'])
        with open(self.config["output_file"], "w", encoding="utf-8") as f:
            f.write(final_text)

        # 添加这一行来保存日志
        debug_output.save_log()

        log_info(f"处理完成！输出文件：{self.config['output_file']}")

import os
from collections import Counter
from datetime import datetime


class DebugOutput:
    def __init__(self, debug, temp_dir, add_timestamp=True):
        """初始化调试输出器 - 专注于调试文件保存功能

        注意：此类的终端输出功能已被移除，现在只负责：
        - 保存处理步骤的中间结果文件
        - 生成处理日志文件
        - 终端和GUI输出由统一日志系统处理
        """
        self.debug = debug
        self.temp_dir = temp_dir
        self.add_timestamp = add_timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S") if add_timestamp else ""

        # 用于自动记录步骤顺序
        self.step_counter = 0
        self.step_order = {}

        # 用于收集日志内容
        self.log_content = []

        # 确保临时目录存在
        if debug and not os.path.exists(temp_dir):
            os.makedirs(temp_dir)

    def show_step(self, step_name, content, stats=None):
        """显示处理步骤的结果"""
        if not self.debug:
            return

        # 为新步骤分配序号（跳过"读入文件"步骤）
        if step_name != "读入文件" and step_name not in self.step_order:
            self.step_counter += 1
            self.step_order[step_name] = self.step_counter

        # 构建并记录日志内容
        log_lines = []

        # 显示统计信息
        if step_name == "读入文件":
            # 从 content 的 stats 中获取文件名（需要在调用时传入）
            input_file = stats.get("input_file", "") if stats else ""
            filename = os.path.basename(input_file) if input_file else ""
            log_lines.append(f"\n已读入文件 {filename}")
            log_lines.append(f"文本长度: {len(content)} 字符")

        elif step_name == "文本清理":
            if stats:
                log_lines.append("\n文本清理统计:")
                log_lines.append("-" * 40)
                if stats.get("special_chars", 0) > 0:
                    log_lines.append(f"移除 BOM 标记: {stats['special_chars']} 处")
                if stats.get("newlines", 0) > 0:
                    log_lines.append(f"统一换行符: {stats['newlines']} 处")
                if stats.get("punctuation", 0) > 0:
                    log_lines.append(f"规范化标点: {stats['punctuation']} 处")
                if stats.get("numbers", 0) > 0:
                    log_lines.append(f"规范化数字: {stats['numbers']} 处")
                if stats.get("spaces", 0) > 0:
                    log_lines.append(f"统一空格: {stats['spaces']} 处")
                if stats.get("empty_lines", 0) > 0:
                    log_lines.append(f"合并空行: {stats['empty_lines']} 处")
                log_lines.append("-" * 40)

        elif step_name == "智能断句":
            if isinstance(content, list):
                log_lines.append(f"\n智能断句统计:")
                log_lines.append("-" * 40)
                log_lines.append(f"共拆分出 {len(content)} 个句子")
                log_lines.append(f"最长句子: {len(max(content, key=len))} 字符")
                log_lines.append(f"最短句子: {len(min(content, key=len))} 字符")
                log_lines.append(
                    f"平均句长: {sum(len(s) for s in content) / len(content):.1f} 字符"
                )
                log_lines.append("-" * 40)

        elif step_name == "停顿词处理":
            if stats:
                log_lines.append("\n停顿词处理统计:")
                log_lines.append("-" * 40)
                total_count = sum(stats.values())
                log_lines.append(f"共处理停顿词 {total_count} 处:")
                for word_type, details in stats.items():
                    if isinstance(details, dict):
                        log_lines.append(f"\n{word_type}:")
                        for word, count in details.items():
                            log_lines.append(f"  - '{word}': {count} 处")
                    else:
                        log_lines.append(f"  - {word_type}: {details} 处")
                log_lines.append("-" * 40)

        elif step_name == "智能断行":
            if isinstance(content, str):
                lines = content.split("\n")
                log_lines.append(f"\n智能断行统计:")
                log_lines.append("-" * 40)
                if len(lines) > 0:
                    log_lines.append(f"  - 总行数: {len(lines)} 行")
                    log_lines.append(f"  - 最长行: {len(max(lines, key=len))} 字符")
                    log_lines.append(f"  - 最短行: {len(min(lines, key=len))} 字符")
                    log_lines.append(
                        f"  - 平均行长: {sum(len(l) for l in lines) / len(lines):.1f} 字符"
                    )
                log_lines.append("-" * 40)

        # 收集日志内容（不输出到终端，由统一日志系统处理）
        for line in log_lines:
            self.log_content.append(line)

        # 保存处理结果文件（跳过"读入文件"步骤）
        if step_name != "读入文件":
            # 获取步骤序号并构建文件名
            step_num = self.step_order[step_name]
            if self.add_timestamp:
                filename = f"{self.timestamp}_{step_num}_{step_name.lower().replace(' ', '_')}.txt"
            else:
                filename = f"{step_num}_{step_name.lower().replace(' ', '_')}.txt"
            filepath = os.path.join(self.temp_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, list):
                    f.write("\n".join(f"{i}. {item}" for i, item in enumerate(content, 1)))
                else:
                    f.write(content)

    def save_log(self):
        """保存处理日志"""
        if self.debug and self.log_content:
            if self.add_timestamp:
                log_filename = f"{self.timestamp}_processing_log.txt"
            else:
                log_filename = "processing_log.txt"
            log_filepath = os.path.join(self.temp_dir, log_filename)

            with open(log_filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_content))

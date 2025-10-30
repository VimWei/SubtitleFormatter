import json
import os
import re
from datetime import datetime


class DebugOutput:
    def __init__(self, debug, debug_dir, add_timestamp=True):
        """初始化调试输出器 - 专注于调试文件保存功能

        注意：此类的终端输出功能已被移除，现在只负责：
        - 保存处理步骤的中间结果文件
        - 生成处理日志文件
        - 终端和GUI输出由统一日志系统处理
        """
        self.debug = debug
        self.debug_dir = debug_dir
        self.add_timestamp = add_timestamp
        self.timestamp = datetime.now().strftime("%Y%m%d%H%M%S") if add_timestamp else ""

        # 用于自动记录步骤顺序
        self.step_counter = 0
        self.step_order = {}

        # 用于收集日志内容
        self.log_content = []

        # 确保调试目录存在
        if debug and not os.path.exists(debug_dir):
            os.makedirs(debug_dir)

    def show_step(self, step_name, content, stats=None):
        """显示并保存每个步骤的中间结果（适配灵活的插件链）

        约定：
        - step_name 可为任意可读名称；若形如 "插件处理: NAME"，将自动提取 NAME 作为插件名以参与文件命名
        - content 可为 str 或 list；其他类型将转为 str
        - stats 若为 dict，则会被以 JSON 侧车文件保存（.stats.json）
        """
        if not self.debug:
            return

        # 为新步骤分配序号（跳过"读入文件"步骤）
        if step_name != "读入文件" and step_name not in self.step_order:
            self.step_counter += 1
            self.step_order[step_name] = self.step_counter

        # 解析插件名（如果是 "插件处理: NAME" 形式）
        plugin_name = None
        m = re.match(r"^插件处理\s*:\s*(.+)$", str(step_name))
        if m:
            plugin_name = m.group(1).strip()

        # 构建并记录日志内容（通用格式）
        log_lines = []

        # 日志抬头
        if step_name == "读入文件":
            input_file = stats.get("input_file", "") if stats else ""
            filename = os.path.basename(input_file) if input_file else ""
            log_lines.append(f"\n已读入文件 {filename}")
        else:
            step_num = self.step_order.get(step_name, 0)
            title = plugin_name if plugin_name else step_name
            log_lines.append(f"\n[{step_num}] {title}")

        # 内容摘要（通用）
        if isinstance(content, list):
            log_lines.append("-" * 40)
            log_lines.append(f"类型: list  | 项数: {len(content)}")
            if content:
                longest = max(content, key=len)
                shortest = min(content, key=len)
                avg_len = sum(len(x) for x in content) / len(content)
                log_lines.append(
                    f"最长项: {len(longest)} 字符  最短项: {len(shortest)} 字符  平均长度: {avg_len:.1f}"
                )
            log_lines.append("-" * 40)
        elif isinstance(content, str):
            log_lines.append("-" * 40)
            log_lines.append(f"类型: str  | 长度: {len(content)} 字符")
            log_lines.append("-" * 40)
        else:
            # 其他类型统一转为字符串并记录类型
            log_lines.append("-" * 40)
            log_lines.append(f"类型: {type(content).__name__}")
            log_lines.append("-" * 40)

        # 若提供 stats，打印其键摘要
        if isinstance(stats, dict) and stats:
            keys_preview = ", ".join(list(stats.keys())[:10])
            log_lines.append(f"统计字段: {keys_preview}")

        # 收集日志内容（不输出到终端，由统一日志系统处理）
        for line in log_lines:
            self.log_content.append(line)

        # 保存处理结果文件（跳过"读入文件"步骤）
        if step_name != "读入文件":
            # 获取步骤序号并构建文件名
            step_num = self.step_order[step_name]

            def _sanitize(value: str) -> str:
                value = value.strip().lower()
                value = re.sub(r"[^0-9a-zA-Z\u4e00-\u9fff]+", "_", value)
                value = re.sub(r"_+", "_", value).strip("_")
                return value or "step"

            base_name = _sanitize(plugin_name) if plugin_name else _sanitize(step_name)
            prefix = f"{self.timestamp}_" if self.add_timestamp else ""
            txt_filename = f"{prefix}{step_num}_{base_name}.txt"
            filepath = os.path.join(self.debug_dir, txt_filename)

            with open(filepath, "w", encoding="utf-8") as f:
                if isinstance(content, list):
                    f.write("\n".join(f"{i}. {item}" for i, item in enumerate(content, 1)))
                elif isinstance(content, str):
                    f.write(content)
                else:
                    f.write(str(content))

            # 如果有统计信息，额外保存一个 JSON 侧车文件
            if isinstance(stats, dict) and stats:
                stats_filename = f"{prefix}{step_num}_{base_name}.stats.json"
                stats_path = os.path.join(self.debug_dir, stats_filename)
                try:
                    with open(stats_path, "w", encoding="utf-8") as sf:
                        json.dump(stats, sf, ensure_ascii=False, indent=2)
                except Exception:
                    # 回退到以文本形式保存
                    with open(stats_path.replace(".json", ".txt"), "w", encoding="utf-8") as sf:
                        for k, v in stats.items():
                            sf.write(f"{k}: {v}\n")

    def save_log(self):
        """保存处理日志"""
        if self.debug and self.log_content:
            if self.add_timestamp:
                log_filename = f"{self.timestamp}_processing_log.txt"
            else:
                log_filename = "processing_log.txt"
            log_filepath = os.path.join(self.debug_dir, log_filename)

            with open(log_filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(self.log_content))

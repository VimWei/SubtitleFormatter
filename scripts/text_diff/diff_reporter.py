"""
差异报告模块
负责生成和输出差异报告
"""

import json
import csv
from typing import List, Dict, Any
from dataclasses import asdict
from sequence_aligner import ComparisonResult, WordDifference, DiffType


class DiffReporter:
    """差异报告器"""
    
    def __init__(self, color_output: bool = True):
        """
        初始化报告器
        
        Args:
            color_output: 是否使用彩色输出
        """
        self.color_output = color_output
        
        if color_output:
            try:
                from colorama import init, Fore, Back, Style
                init(autoreset=True)
                self.Fore = Fore
                self.Back = Back
                self.Style = Style
            except ImportError:
                self.color_output = False
                self.Fore = self.Back = self.Style = None
    
    def print_console_report(self, result: ComparisonResult, 
                           old_file: str, new_file: str, 
                           show_context: int = 3):
        """
        打印控制台报告
        
        Args:
            result: 比较结果
            old_file: 旧文件名
            new_file: 新文件名
            show_context: 显示上下文行数
        """
        print(f"\n{'='*60}")
        print(f"文件差异比较报告")
        print(f"{'='*60}")
        print(f"旧文件: {old_file}")
        print(f"新文件: {new_file}")
        print(f"{'='*60}")
        
        # 打印统计信息
        self._print_statistics(result)
        
        # 不显示差异详情，只显示统计信息
        if result.differences:
            print(f"\n{self._colorize(f'发现 {result.total_differences} 个差异', 'yellow')}")
        else:
            print(f"\n{self._colorize('✓ 未发现词汇差异', 'green')}")
    
    def _print_statistics(self, result: ComparisonResult):
        """打印统计信息"""
        print(f"\n统计信息:")
        print(f"  总差异数: {self._colorize(str(result.total_differences), 'red')}")
        print(f"  插入: {self._colorize(str(result.insertions), 'green')}")
        print(f"  删除: {self._colorize(str(result.deletions), 'red')}")
        print(f"  替换: {self._colorize(str(result.replacements), 'yellow')}")
        print(f"  相同词汇: {self._colorize(str(result.equal_words), 'blue')}")
        print(f"  相似度: {self._colorize(f'{result.similarity_ratio:.2%}', 'blue')}")
    
    def _print_differences(self, differences: List[WordDifference], show_context: int):
        """打印差异详情"""
        for i, diff in enumerate(differences, 1):
            print(f"\n差异 #{i}:")
            
            if diff.type == DiffType.INSERT:
                print(f"  类型: {self._colorize('插入', 'green')}")
                print(f"  位置: 新文件第{diff.new_line}行第{diff.new_column}列")
                print(f"  内容: {self._colorize(f'+ {diff.new_word}', 'green')}")
                
            elif diff.type == DiffType.DELETE:
                print(f"  类型: {self._colorize('删除', 'red')}")
                print(f"  位置: 旧文件第{diff.old_line}行第{diff.old_column}列")
                print(f"  内容: {self._colorize(f'- {diff.old_word}', 'red')}")
                
            elif diff.type == DiffType.REPLACE:
                print(f"  类型: {self._colorize('替换', 'yellow')}")
                print(f"  位置: 旧文件第{diff.old_line}行第{diff.old_column}列")
                print(f"  内容: {self._colorize(f'- {diff.old_word}', 'red')} → {self._colorize(f'+ {diff.new_word}', 'green')}")
    
    def _colorize(self, text: str, color: str) -> str:
        """为文本添加颜色"""
        if not self.color_output or not self.Fore:
            return text
        
        color_map = {
            'red': self.Fore.RED,
            'green': self.Fore.GREEN,
            'yellow': self.Fore.YELLOW,
            'blue': self.Fore.BLUE,
            'cyan': self.Fore.CYAN,
            'magenta': self.Fore.MAGENTA,
            'white': self.Fore.WHITE,
            'bright_red': self.Fore.LIGHTRED_EX,
            'bright_green': self.Fore.LIGHTGREEN_EX,
            'bright_yellow': self.Fore.LIGHTYELLOW_EX,
            'bright_blue': self.Fore.LIGHTBLUE_EX,
            'bright_cyan': self.Fore.LIGHTCYAN_EX,
            'bright_magenta': self.Fore.LIGHTMAGENTA_EX,
            'bright_white': self.Fore.LIGHTWHITE_EX
        }
        
        return f"{color_map.get(color, '')}{text}{self.Style.RESET_ALL if self.Style else ''}"
    
    def save_json_report(self, result: ComparisonResult, filename: str):
        """
        保存JSON格式报告
        
        Args:
            result: 比较结果
            filename: 输出文件名
        """
        # 转换结果为可序列化的格式
        data = {
            'statistics': {
                'total_differences': result.total_differences,
                'insertions': result.insertions,
                'deletions': result.deletions,
                'replacements': result.replacements,
                'equal_words': result.equal_words,
                'similarity_ratio': result.similarity_ratio
            },
            'differences': []
        }
        
        for diff in result.differences:
            diff_data = asdict(diff)
            diff_data['type'] = diff.type.value  # 转换枚举为字符串
            data['differences'].append(diff_data)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"JSON报告已保存到: {filename}")
    
    def save_csv_report(self, result: ComparisonResult, filename: str):
        """
        保存CSV格式报告
        
        Args:
            result: 比较结果
            filename: 输出文件名
        """
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入标题行
            writer.writerow([
                '序号', '类型', '旧词汇', '新词汇', 
                '旧文件行号', '旧文件列号', '新文件行号', '新文件列号'
            ])
            
            # 写入差异数据
            for i, diff in enumerate(result.differences, 1):
                writer.writerow([
                    i,
                    diff.type.value,
                    diff.old_word,
                    diff.new_word,
                    diff.old_line,
                    diff.old_column,
                    diff.new_line,
                    diff.new_column
                ])
        
        print(f"CSV报告已保存到: {filename}")
    
    def save_html_report(self, result: ComparisonResult, filename: str, 
                        old_file: str, new_file: str):
        """
        保存HTML格式报告
        
        Args:
            result: 比较结果
            filename: 输出文件名
            old_file: 旧文件名
            new_file: 新文件名
        """
        html_content = self._generate_html_content(result, old_file, new_file)
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML报告已保存到: {filename}")
    
    def _generate_html_content(self, result: ComparisonResult, 
                              old_file: str, new_file: str) -> str:
        """生成HTML内容"""
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>文件差异比较报告</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 2px solid #007acc;
            padding-bottom: 10px;
        }}
        .stats {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .stats h3 {{
            margin-top: 0;
            color: #495057;
        }}
        .stat-item {{
            display: inline-block;
            margin: 5px 15px 5px 0;
            padding: 5px 10px;
            border-radius: 3px;
            font-weight: bold;
        }}
        .stat-total {{ background: #dc3545; color: white; }}
        .stat-insert {{ background: #28a745; color: white; }}
        .stat-delete {{ background: #dc3545; color: white; }}
        .stat-replace {{ background: #ffc107; color: black; }}
        .stat-equal {{ background: #17a2b8; color: white; }}
        .stat-similarity {{ background: #6f42c1; color: white; }}
        .diff-item {{
            margin: 15px 0;
            padding: 15px;
            border-left: 4px solid #ccc;
            background: #f8f9fa;
        }}
        .diff-insert {{ border-left-color: #28a745; }}
        .diff-delete {{ border-left-color: #dc3545; }}
        .diff-replace {{ border-left-color: #ffc107; }}
        .diff-type {{
            font-weight: bold;
            margin-bottom: 10px;
        }}
        .diff-insert .diff-type {{ color: #28a745; }}
        .diff-delete .diff-type {{ color: #dc3545; }}
        .diff-replace .diff-type {{ color: #ffc107; }}
        .diff-content {{
            font-family: 'Courier New', monospace;
            background: #e9ecef;
            padding: 10px;
            border-radius: 3px;
            margin: 5px 0;
        }}
        .diff-old {{ color: #dc3545; }}
        .diff-new {{ color: #28a745; }}
        .no-diff {{
            text-align: center;
            color: #28a745;
            font-size: 1.2em;
            margin: 40px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>文件差异比较报告</h1>
        
        <div class="stats">
            <h3>文件信息</h3>
            <p><strong>旧文件:</strong> {old_file}</p>
            <p><strong>新文件:</strong> {new_file}</p>
            
            <h3>统计信息</h3>
            <span class="stat-item stat-total">总差异: {result.total_differences}</span>
            <span class="stat-item stat-insert">插入: {result.insertions}</span>
            <span class="stat-item stat-delete">删除: {result.deletions}</span>
            <span class="stat-item stat-replace">替换: {result.replacements}</span>
            <span class="stat-item stat-equal">相同: {result.equal_words}</span>
            <span class="stat-item stat-similarity">相似度: {result.similarity_ratio:.2%}</span>
        </div>
"""
        
        if result.differences:
            html += "<h2>差异详情</h2>\n"
            for i, diff in enumerate(result.differences, 1):
                diff_class = f"diff-{diff.type.value}"
                html += f"""
        <div class="diff-item {diff_class}">
            <div class="diff-type">差异 #{i}: {diff.type.value.upper()}</div>
"""
                
                if diff.type == DiffType.INSERT:
                    html += f"""
            <p><strong>位置:</strong> 新文件第{diff.new_line}行第{diff.new_column}列</p>
            <div class="diff-content diff-new">+ {diff.new_word}</div>
"""
                elif diff.type == DiffType.DELETE:
                    html += f"""
            <p><strong>位置:</strong> 旧文件第{diff.old_line}行第{diff.old_column}列</p>
            <div class="diff-content diff-old">- {diff.old_word}</div>
"""
                elif diff.type == DiffType.REPLACE:
                    html += f"""
            <p><strong>位置:</strong> 旧文件第{diff.old_line}行第{diff.old_column}列</p>
            <div class="diff-content diff-old">- {diff.old_word}</div>
            <div class="diff-content diff-new">+ {diff.new_word}</div>
"""
                
                html += "        </div>\n"
        else:
            html += '<div class="no-diff">✓ 未发现词汇差异</div>\n'
        
        html += """
    </div>
</body>
</html>
"""
        return html

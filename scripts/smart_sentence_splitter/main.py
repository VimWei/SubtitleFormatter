#!/usr/bin/env python3
"""
智能句子拆分工具 - 将长句和复合句拆分为更短的句子
基于规则和启发式方法，无需LLM即可实现智能拆分
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional


class SmartSentenceSplitter:
    """智能句子拆分器"""

    def __init__(self):
        # 连接词列表 - 用于识别复合句的拆分点
        self.conjunctions = {
            # 并列连接词
            'and', 'or', 'but', 'yet', 'so', 'for', 'nor',
            # 从属连接词
            'because', 'since', 'as', 'if', 'when', 'while', 'although', 'though', 'unless', 'until', 'before', 'after',
            # 其他连接词
            'however', 'therefore', 'moreover', 'furthermore', 'nevertheless', 'meanwhile', 'consequently',
            'additionally', 'similarly', 'likewise', 'otherwise', 'instead', 'rather', 'indeed',
            # 从句引导词
            'which', 'that', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how',
            # 时间/条件连接词
            'then', 'next', 'finally', 'meanwhile', 'subsequently',
            # 短语连接词
            'such as', 'as well as', 'in order to', 'so that', 'in case', 'provided that',
            'even though', 'as though', 'as if'
        }
        
        # 标点符号优先级（用于确定最佳拆分点）
        self.punctuation_priority = {
            ';': 5,  # 分号优先级最高
            ':': 4,  # 冒号次之
            ',': 3,  # 逗号第三
        }
        
        # 连接词优先级
        self.conjunction_priority = {
            # 高优先级连接词
            'however': 2, 'therefore': 2, 'moreover': 2, 'furthermore': 2, 
            'nevertheless': 2, 'meanwhile': 2, 'consequently': 2,
            # 中优先级连接词  
            'because': 1, 'since': 1, 'although': 1, 'though': 1, 
            'unless': 1, 'until': 1, 'before': 1, 'after': 1,
            # 低优先级连接词
            'and': 0, 'or': 0, 'but': 0, 'yet': 0, 'so': 0, 'for': 0, 'nor': 0,
        }
        
        # 数字格式模式（用于排除数字中的逗号）
        self.number_patterns = [
            r'\d{1,3}(,\d{3})*',  # 千位分隔符：1,000,000
            r'\d+\.\d+',          # 小数：3.14
            r'\$\d+(,\d{3})*',    # 货币：$1,000
        ]
        
        # 简单并列模式（用于排除简单的词汇并列）
        self.simple_enumeration_patterns = [
            r'\b\w+\s*,\s*\w+\s*,\s*\w+\b',  # 三个或更多简单词汇并列
            r'\b\w+\s*,\s*(?!and|or|but|yet|so|for|nor|because|since|as|if|when|while|although|though|unless|until|before|after|however|therefore|moreover|furthermore|nevertheless|meanwhile|consequently|additionally|similarly|likewise|otherwise|instead|rather|indeed|which|that|who|whom|whose|where|when|why|how|then|next|finally|subsequently|a|an|the|this|that|these|those)\w+\b',  # 两个简单词汇并列，但排除连接词和冠词
        ]

    def is_number_context(self, text: str, pos: int) -> bool:
        """检查逗号是否在数字上下文中"""
        # 检查前后是否有数字
        before = text[:pos].rstrip()
        after = text[pos+1:].lstrip()
        
        # 检查是否匹配数字模式
        for pattern in self.number_patterns:
            if re.search(pattern, text[max(0, pos-20):pos+20]):
                return True
        return False

    def is_simple_enumeration(self, text: str, pos: int) -> bool:
        """检查逗号是否在简单并列中"""
        # 获取逗号前后的上下文
        context_start = max(0, pos - 50)
        context_end = min(len(text), pos + 50)
        context = text[context_start:context_end]
        
        for pattern in self.simple_enumeration_patterns:
            if re.search(pattern, context):
                return True
        return False

    def _is_in_subordinate_clause(self, sentence: str, pos: int) -> bool:
        """检查位置是否在从句中"""
        # 查找最近的从句引导词
        subordinate_markers = ['which', 'that', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how']
        
        # 检查位置前是否有从句引导词
        before_pos = sentence[:pos].lower()
        for marker in subordinate_markers:
            marker_pos = before_pos.rfind(marker)
            if marker_pos != -1:
                # 检查从句引导词前是否有逗号
                before_marker = sentence[:marker_pos]
                if ',' in before_marker:
                    # 这是一个从句，检查位置是否在从句内部
                    # 查找从句的结束位置（下一个逗号或句号）
                    after_marker = sentence[marker_pos + len(marker):]
                    # 简单检查：如果位置在从句引导词后，且在下一个主要标点前
                    if pos > marker_pos + len(marker):
                        return True
        
        return False

    def find_split_points(self, sentence: str) -> List[Tuple[int, int, str]]:
        """
        找到句子中的拆分点
        
        Returns:
            List of (position, priority, reason) tuples
        """
        split_points = []
        
        # 查找标点符号拆分点
        for punct, priority in self.punctuation_priority.items():
            for match in re.finditer(re.escape(punct), sentence):
                pos = match.start()
                
                # 排除数字上下文中的逗号
                if punct == ',' and self.is_number_context(sentence, pos):
                    continue
                    
                # 排除简单并列中的逗号
                if punct == ',' and self.is_simple_enumeration(sentence, pos):
                    continue
                
                # 检查逗号后是否有连接词
                if punct == ',':
                    # 检查逗号后是否跟着连接词
                    after_comma = sentence[pos+1:].strip()
                    found_conjunction = False
                    for conjunction in self.conjunctions:
                        if after_comma.lower().startswith(conjunction + ' '):
                            # 在连接词前拆分
                            conjunction_pos = pos + 1 + after_comma.lower().find(conjunction)
                            # 检查是否在从句中
                            if not self._is_in_subordinate_clause(sentence, conjunction_pos):
                                split_points.append((conjunction_pos, priority + 2, f"逗号+连接词: {conjunction}"))
                                found_conjunction = True
                                break
                    
                    # 如果没有找到连接词，检查其他常见模式
                    if not found_conjunction:
                        # 检查 ", then", ", so", ", which" 等模式
                        comma_patterns = [
                            r',\s+then\s+', r',\s+so\s+', r',\s+which\s+', r',\s+that\s+',
                            r',\s+where\s+', r',\s+when\s+', r',\s+who\s+', r',\s+why\s+',
                            r',\s+how\s+', r',\s+next\s+', r',\s+finally\s+',
                            r',\s+such\s+as\s+', r',\s+as\s+well\s+as\s+', r',\s+in\s+order\s+to\s+',
                            r',\s+so\s+that\s+', r',\s+in\s+case\s+', r',\s+provided\s+that\s+',
                            r',\s+and\s+also\s+', r',\s+but\s+that\s+', r',\s+or\s+if\s+',
                            r',\s+even\s+though\s+', r',\s+although\s+', r',\s+though\s+',
                            r',\s+because\s+', r',\s+since\s+', r',\s+unless\s+', r',\s+until\s+',
                            r',\s+before\s+', r',\s+after\s+', r',\s+while\s+', r',\s+if\s+',
                            r',\s+and\s+if\s+', r',\s+or\s+if\s+', r',\s+but\s+if\s+',
                            r',\s+when\s+if\s+', r',\s+where\s+if\s+'
                        ]
                        for pattern in comma_patterns:
                            if re.search(pattern, sentence[pos:pos+50], re.IGNORECASE):
                                # 检查是否在从句中
                                if not self._is_in_subordinate_clause(sentence, pos):
                                    # 在逗号后拆分
                                    split_points.append((pos, priority + 2, f"逗号+模式: {pattern}"))
                                    found_conjunction = True
                                    break
                    
                    if not found_conjunction:
                        # 普通逗号拆分 - 只在非从句中进行
                        if not self._is_in_subordinate_clause(sentence, pos):
                            split_points.append((pos, priority, f"标点符号: {punct}"))
                else:
                    split_points.append((pos, priority, f"标点符号: {punct}"))
        
        # 查找连接词拆分点
        sentence_lower = sentence.lower()
        for conjunction in self.conjunctions:
            # 查找连接词在句子中的位置
            pos = 0
            while True:
                pos = sentence_lower.find(conjunction, pos)
                if pos == -1:
                    break
                # 确保是完整的单词，并且不在句子开头
                if pos > 0 and (pos == 0 or not sentence_lower[pos-1].isalnum()) and \
                   (pos + len(conjunction) >= len(sentence_lower) or not sentence_lower[pos + len(conjunction)].isalnum()):
                    # 检查连接词前后是否有足够的内容
                    before_conjunction = sentence[:pos].strip()
                    after_conjunction = sentence[pos + len(conjunction):].strip()
                    
                    # 只有当连接词前后都有足够内容时才拆分
                    if len(before_conjunction) > 20 and len(after_conjunction) > 20:
                        # 额外检查：避免拆分从句中的连接词
                        if not self._is_in_subordinate_clause(sentence, pos):
                            # 使用连接词优先级
                            priority = self.conjunction_priority.get(conjunction, 0)
                            split_points.append((pos, priority, f"连接词: {conjunction}"))
                pos += len(conjunction)
        
        # 按位置排序
        split_points.sort(key=lambda x: x[0])
        return split_points

    def should_split_sentence(self, sentence: str) -> bool:
        """判断句子是否需要拆分"""
        # 长度阈值
        if len(sentence) < 60:  # 进一步降低长度阈值
            return False
        
        # 检查是否包含不应该拆分的模式
        problematic_patterns = [
            r'which.*which.*and.*which',  # 多个which从句
            r'who.*when.*and',  # who...when...and模式
            r'which.*\$.*and.*which',  # 包含金额的which从句
            # 移除过于宽泛的 even though 模式，因为 ", even though" 是好的拆分点
        ]
        
        for pattern in problematic_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return False
            
        # 检查是否有拆分点
        split_points = self.find_split_points(sentence)
        return len(split_points) > 0

    def split_sentence(self, sentence: str, depth: int = 0) -> List[str]:
        """拆分单个句子"""
        # 防止递归过深
        if depth > 3:  # 减少最大递归深度
            return [sentence]
            
        if not self.should_split_sentence(sentence):
            return [sentence]
        
        split_points = self.find_split_points(sentence)
        if not split_points:
            return [sentence]
        
        # 选择最佳拆分点（优先级最高的第一个）
        best_split = min(split_points, key=lambda x: (-x[1], x[0]))
        split_pos = best_split[0]
        
        # 若在逗号处分行，确保将逗号与其后的一个空格保留在上一行
        if 0 <= split_pos < len(sentence):
            if sentence[split_pos] == ',':
                split_pos += 1
                if split_pos < len(sentence) and sentence[split_pos] == ' ':  # 保留一个空格在上一行
                    split_pos += 1
            elif sentence[split_pos] == ' ' and split_pos > 0 and sentence[split_pos - 1] == ',':
                # 如果正好在逗号后的空格处分行，则跳过这个空格
                split_pos += 1

        # 拆分句子（不修改任何标点或空白，只做换行）
        part1 = sentence[:split_pos]
        part2 = sentence[split_pos:]
        
        # 确保第二部分以大写字母开头或保持原样（仅用于逻辑判断，输出不改动文本）
        part2_for_logic = part2.lstrip()
        if part2_for_logic and part2_for_logic[0].islower():
            # 如果第二部分以小写字母开头，说明可能缺少了开头的单词
            # 特殊处理：检查是否是 "then" 或其他重要连接词开头
            important_starters = ['then', 'so', 'because', 'since', 'when', 'where', 'while', 'though', 'although']
            is_important_starter = any(part2_for_logic.lower().startswith(starter + ' ') for starter in important_starters)
            
            if is_important_starter:
                # 对于重要连接词开头的句子，仍然进行拆分，并且递归处理
                result = []
                if part1 and len(part1) > 15:
                    result.extend(self.split_sentence(part1, depth + 1))
                elif part1:
                    result.append(part1)
                    
                if part2 and len(part2) > 15:
                    result.extend(self.split_sentence(part2, depth + 1))
                elif part2:
                    result.append(part2)
                
                return result if result else [sentence]
            
            # 在这种情况下，我们只拆分一次，不再递归
            # 但是仍然进行拆分，只是不递归
            # 只有当第二部分足够长时才拆分
            if len(part2.strip()) > 20:
                # 对于长句子，即使第二部分以小写字母开头，也尝试进一步拆分
                if len(part2.strip()) > 80:  # 降低阈值
                    # 尝试对第二部分进行拆分
                    part2_split = self.split_sentence(part2, depth + 1)
                    if len(part2_split) > 1:
                        return [part1] + part2_split
                    else:
                        return [part1, part2]
                else:
                    return [part1, part2]
            else:
                return [sentence]
        
        # 检查拆分后的部分是否太短（避免单个连接词成行）
        if len(part1.strip()) < 5 or len(part2.strip()) < 5:
            return [sentence]
        
        # 递归拆分
        result = []
        if part1 and len(part1) > 15:  # 降低第一部分长度要求
            result.extend(self.split_sentence(part1, depth + 1))
        elif part1:
            result.append(part1)
            
        if part2 and len(part2) > 15:  # 降低第二部分长度要求
            result.extend(self.split_sentence(part2, depth + 1))
        elif part2:
            result.append(part2)
        
        return result if result else [sentence]

    def process_sentences(self, sentences: List[str]) -> List[str]:
        """处理句子列表"""
        result = []
        for sentence in sentences:
            if sentence.strip():
                split_sentences = self.split_sentence(sentence.strip())
                result.extend(split_sentences)
        return result

    def process_file(self, input_file: Path, output_file: Path = None) -> None:
        """处理文件"""
        try:
            # 读取输入文件
            with open(input_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # 处理每一行（每行一个句子）
            all_sentences = []
            for line in lines:
                line = line.strip()
                if line:
                    all_sentences.append(line)
            
            # 智能拆分
            processed_sentences = self.process_sentences(all_sentences)
            
            # 如果没有指定输出文件，自动生成
            if output_file is None:
                input_stem = input_file.stem
                output_file = Path("data/output") / f"{input_stem}.smart_split.txt"
                output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入输出文件
            with open(output_file, "w", encoding="utf-8") as f:
                for sentence in processed_sentences:
                    f.write(sentence + "\n")
            
            print(f"✅ 处理完成:")
            print(f"   原始句子数: {len(all_sentences)}")
            print(f"   拆分后句子数: {len(processed_sentences)}")
            print(f"   输出文件: {output_file}")
            
        except FileNotFoundError:
            print(f"❌ 错误：找不到输入文件 {input_file}")
            sys.exit(1)
        except Exception as e:
            print(f"❌ 处理文件时出错: {e}")
            sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="智能句子拆分工具 - 将长句和复合句拆分为更短的句子",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python main.py input.txt                    # 自动保存到 data/output/
  python main.py input.txt -o output.txt      # 自定义输出文件
  python main.py input.txt --output output.txt # 自定义输出文件

功能特点:
  - 基于规则和启发式方法，无需LLM
  - 识别连接词和标点符号进行智能拆分
  - 排除数字格式和简单并列的误拆分
  - 支持递归拆分，处理复杂复合句
        """,
    )

    parser.add_argument("input_file", help="输入文本文件路径（每行一个句子）")
    parser.add_argument(
        "-o", "--output", dest="output_file", help="输出文件路径（可选，不指定则自动生成）"
    )
    parser.add_argument("--version", action="version", version="智能句子拆分工具 v1.0.0")

    args = parser.parse_args()

    # 验证输入文件
    input_path = Path(args.input_file)
    if not input_path.exists():
        print(f"❌ 错误：输入文件不存在: {input_path}")
        sys.exit(1)

    if not input_path.is_file():
        print(f"❌ 错误：输入路径不是文件: {input_path}")
        sys.exit(1)

    # 处理输出文件路径
    output_path = None
    if args.output_file:
        output_path = Path(args.output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    # 创建拆分器并处理文件
    splitter = SmartSentenceSplitter()
    splitter.process_file(input_path, output_path)


if __name__ == "__main__":
    main()

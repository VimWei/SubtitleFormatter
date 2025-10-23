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

    def __init__(self, min_recursive_length: int = 70, max_depth: int = 8):
        # 递归控制参数
        self.min_recursive_length = min_recursive_length  # 最小递归长度阈值
        self.max_depth = max_depth  # 最大递归深度
        
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
            # 从句引导词（中等优先级）
            'that': 1, 'which': 1, 'who': 1, 'whom': 1, 'whose': 1, 'where': 1, 'when': 1, 'why': 1, 'how': 1,
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
            r'\b\w+\s*,\s*(?!and|or|but|yet|so|for|nor|because|since|as|if|when|while|although|though|unless|until|before|after|however|therefore|moreover|furthermore|nevertheless|meanwhile|consequently|additionally|similarly|likewise|otherwise|instead|rather|indeed|which|that|who|whom|whose|where|when|why|how|then|next|finally|subsequently|a|an|the|this|that|these|those|you|we|they|he|she|it|i|me|us|them|him|her|might|could|would|should|will|can|may|must|shall)\w+\b',  # 两个简单词汇并列，但排除连接词、冠词、代词和助动词
        ]

    def is_number_context(self, text: str, pos: int) -> bool:
        """检查逗号是否在数字上下文中"""
        # 获取逗号前后的内容
        before = text[:pos].rstrip()
        after = text[pos+1:].lstrip()
        
        # 检查逗号前后是否都是数字（千位分隔符情况）
        if before and after:
            # 检查逗号前是否有数字结尾
            before_match = re.search(r'\d+$', before)
            # 检查逗号后是否有数字开头
            after_match = re.search(r'^\d+', after)
            
            if before_match and after_match:
                return True
        
        # 检查是否在货币格式中（如 $3,000, €1,000, £500 等）
        if pos > 0:
            # 检查逗号前是否有货币符号
            currency_symbols = ['$', '€', '£', '¥', '₹', '₽', '₩', '₪', '₨', '₦', '₡', '₱', '₫', '₴', '₸', '₼', '₾', '₿']
            if text[pos-1] in currency_symbols:
                # 检查逗号后是否有数字
                after_match = re.search(r'^\d+', after)
                if after_match:
                    return True
        
        # 检查是否在数字模式中（如 1,000,000 或 3,000）
        # 使用更精确的正则表达式检查逗号是否在数字中间
        context = text[max(0, pos-10):pos+10]
        number_patterns = [
            r'\d{1,3}(,\d{3})+',  # 千位分隔符：1,000 或 1,000,000
            r'\d+,\d{3}',         # 简单千位分隔符：3,000
        ]
        
        for pattern in number_patterns:
            if re.search(pattern, context):
                return True
        
        return False

    def is_simple_enumeration(self, text: str, pos: int) -> bool:
        """检查逗号是否在简单并列中 - 仅基于词汇数量判断"""
        # 首先检查是否在数字上下文中，如果是则不认为是简单并列
        if self.is_number_context(text, pos):
            return False
        
        # 获取逗号前后的词汇
        before_text = text[:pos].strip()
        after_text = text[pos+1:].strip()
        
        # 提取逗号前后的词汇（去除标点）
        before_words = re.findall(r'\b\w+\b', before_text)
        after_words = re.findall(r'\b\w+\b', after_text)
        
        # 简单判断：如果逗号前后都只有1-2个词汇，且总词汇数不超过6个，则认为是简单并列
        total_words = len(before_words) + len(after_words)
        if total_words <= 6 and len(before_words) <= 2 and len(after_words) <= 2:
            return True
        
        return False
    

    def _is_valid_split_point(self, sentence: str, pos: int) -> bool:
        """检查拆分点是否合适"""
        # 检查拆分后两部分是否都足够长
        part1 = sentence[:pos].strip()
        part2 = sentence[pos:].strip()
        
        # 第一部分至少15字符，第二部分至少15字符
        # 这已经自动排除了句首（<15字符）和句尾（<15字符）的情况
        if len(part1) < 15 or len(part2) < 15:
            return False
        
        # 检查拆分点是否在标点符号上（标点符号拆分需要特殊处理）
        if pos < len(sentence) and sentence[pos] in '.,;:':
            # 对于标点符号，检查后面是否有足够内容
            after_punct = sentence[pos+1:].strip()
            if len(after_punct) < 10:  # 标点后至少10字符
                return False
        
        return True

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
                    # 如果位置在从句引导词之后，则认为在从句中
                    if pos > marker_pos:
                        return True
        
        return False

    def find_split_points(self, sentence: str) -> List[Tuple[int, int, str]]:
        """
        找到句子中的拆分点
        
        Returns:
            List of (position, priority, reason) tuples
        """
        split_points = []

        # 句首从属连接词专门规则：若句子以从属连接词开头，优先使用第一个逗号作为候选
        leading_subordinators = [
            'while', 'although', 'though', 'when', 'if', 'since', 'because',
            'as', 'whereas', 'once', 'after', 'before', 'until', 'unless'
        ]
        stripped = sentence.lstrip()
        stripped_lower = stripped.lower()
        starts_with_subordinator = any(
            stripped_lower.startswith(w + ' ') or stripped_lower.startswith(w + ',')
            for w in leading_subordinators
        )
        # 排除条件句开头的 if（如 "if it needs to..."）
        if starts_with_subordinator and stripped_lower.startswith('if '):
            # 检查是否是条件句（通常后面跟着主语+动词）
            after_if = stripped[3:].strip()
            if after_if and after_if.lower().startswith(('you', 'we', 'they', 'i', 'he', 'she', 'it')):
                starts_with_subordinator = False
        first_comma_pos = sentence.find(',')
        
        # 查找标点符号拆分点
        for punct, priority in self.punctuation_priority.items():
            for match in re.finditer(re.escape(punct), sentence):
                pos = match.start()
                
                # 排除数字上下文中的逗号
                if punct == ',' and self.is_number_context(sentence, pos):
                    continue
                    
                # 排除简单并列中的逗号（但若是句首从属从句的第一个逗号，则保留）
                is_first_comma = (pos == first_comma_pos)
                if punct == ',' and self.is_simple_enumeration(sentence, pos) \
                   and not (starts_with_subordinator and is_first_comma):
                    continue
                
                # 检查逗号后是否有连接词
                if punct == ',':
                    # 检查逗号后是否跟着连接词
                    after_comma = sentence[pos+1:].strip()
                    found_conjunction = False
                    # 优先提升以从句引导词开头的逗号拆分点（that/which/who/where/when/why/how 等）
                    elevated_after = {
                        'that', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how'
                    }
                    for conjunction in self.conjunctions:
                        if after_comma.lower().startswith(conjunction + ' '):
                            # 在逗号处拆分（逗号+连接词模式）
                            # 检查是否在从句中
                            if not self._is_in_subordinate_clause(sentence, pos):
                                boost = 6 if conjunction in elevated_after else 2
                                split_points.append((pos, priority + boost, f"逗号+连接词: {conjunction}"))
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
                                    # 在逗号后拆分；若是 ", that/which/who/..." 等从句开头，进一步提升优先级
                                    if re.match(r',\s+(that|which|who|whom|whose|where|when|why|how)\s+', sentence[pos:pos+50], re.IGNORECASE):
                                        split_points.append((pos, priority + 6, f"逗号+从句: {pattern}"))
                                    else:
                                        split_points.append((pos, priority + 2, f"逗号+模式: {pattern}"))
                                    found_conjunction = True
                                    break
                    
                    if not found_conjunction:
                        # 普通逗号拆分 - 只在非从句中进行
                        if not self._is_in_subordinate_clause(sentence, pos):
                            # 若是句首从属从句的第一个逗号，提高优先级
                            boosted_priority = priority + 3 if (starts_with_subordinator and is_first_comma) else priority
                            reason = "句首从属从句: ," if (starts_with_subordinator and is_first_comma) else f"标点符号: {punct}"
                            split_points.append((pos, boosted_priority, reason))
                else:
                    split_points.append((pos, priority, f"标点符号: {punct}"))
        
        # 查找连接词拆分点
        sentence_lower = sentence.lower()
        
        # 排除短语连接词中的单词，避免重复拆分
        phrase_conjunctions = ['such as', 'as well as', 'in order to', 'so that', 'in case', 'provided that', 'even though', 'as though', 'as if']
        excluded_words = set()
        for phrase in phrase_conjunctions:
            if phrase in sentence_lower:
                words = phrase.split()
                excluded_words.update(words)
        
        for conjunction in self.conjunctions:
            # 跳过短语连接词中的单词
            if conjunction in excluded_words:
                continue
            # 跳过短语连接词本身
            if conjunction in phrase_conjunctions:
                continue
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
        
        # 检查是否包含不应该拆分的模式（已移除特例化规则，统一走长度/优先级策略）
        problematic_patterns = []
        
        for pattern in problematic_patterns:
            if re.search(pattern, sentence, re.IGNORECASE):
                return False
            
        # 检查是否有拆分点
        split_points = self.find_split_points(sentence)
        if len(split_points) > 0:
            return True
        
        # 兜底规则：如果没有找到拆分点，但句子中间有逗号，且拆分后两部分都不太短，则允许拆分
        import re
        comma_matches = list(re.finditer(r',', sentence))
        if len(comma_matches) > 0:
            # 排除句末的逗号（逗号后直接跟着句末标点）
            for match in comma_matches:
                pos = match.start()
                # 检查逗号后是否还有内容（不是句末逗号）
                after_comma = sentence[pos+1:].strip()
                if after_comma:
                    # 检查是否是句末逗号：逗号后只有很少内容且以句末标点结尾
                    after_comma_no_space = after_comma.lstrip()
                    if after_comma_no_space and len(after_comma_no_space) > 10:  # 逗号后有足够的内容
                        # 检查拆分后的两部分长度
                        part1 = sentence[:pos].strip()
                        part2 = after_comma
                        if len(part1) >= 20 and len(part2) >= 20:  # 两部分都不太短
                            return True
        
        return False

    def split_sentence(self, sentence: str, depth: int = 0) -> List[str]:
        """拆分单个句子"""
        # 递归停止条件：深度超限或长度不足
        if depth >= self.max_depth or len(sentence) < self.min_recursive_length:
            return [sentence]
            
        if not self.should_split_sentence(sentence):
            return [sentence]
        
        split_points = self.find_split_points(sentence)
        if not split_points:
            # 兜底规则：如果没有找到拆分点，但句子中间有逗号，且拆分后两部分都不太短，则使用逗号拆分
            import re
            comma_matches = list(re.finditer(r',', sentence))
            for match in comma_matches:
                pos = match.start()
                # 检查逗号后是否还有内容（不是句末逗号）
                after_comma = sentence[pos+1:].strip()
                if after_comma:
                    # 检查是否是句末逗号：逗号后只有很少内容且以句末标点结尾
                    after_comma_no_space = after_comma.lstrip()
                    if after_comma_no_space and len(after_comma_no_space) > 10:  # 逗号后有足够的内容
                        # 检查拆分后的两部分长度
                        part1 = sentence[:pos].strip()
                        part2 = after_comma
                        if len(part1) >= 20 and len(part2) >= 20:  # 两部分都不太短
                            # 使用逗号作为拆分点
                            split_pos = pos
                            # 跳过逗号和空格
                            split_pos += 1
                            if split_pos < len(sentence) and sentence[split_pos] == ' ':
                                split_pos += 1
                            break
            else:
                return [sentence]
        else:
            # 选择最佳拆分点（优先级最高的，如果优先级相同则选择位置最靠左的）
            # 智能筛选：排除句首、句尾、过短片段等不合适的拆分点
            valid_splits = []
            for pos, priority, reason in split_points:
                # 检查拆分点是否合适
                if self._is_valid_split_point(sentence, pos):
                    valid_splits.append((pos, priority, reason))
            
            if valid_splits:
                # 如果有有效拆分点，从中选择最佳的
                best_split = max(valid_splits, key=lambda x: (x[1], -x[0]))
            else:
                # 如果没有有效拆分点，使用原来的逻辑
                best_split = max(split_points, key=lambda x: (x[1], -x[0]))
            
            split_pos = best_split[0]
        
        # 若在逗号处分行，确保将逗号与其后的一个空格保留在上一行
        if 0 <= split_pos < len(sentence):
            if sentence[split_pos] == ',':
                # 检查逗号后是否跟着从句引导词
                after_comma = sentence[split_pos+1:].strip()
                subordinate_markers = ['that', 'which', 'who', 'whom', 'whose', 'where', 'when', 'why', 'how']
                is_subordinate = any(after_comma.lower().startswith(marker + ' ') for marker in subordinate_markers)
                
                if is_subordinate:
                    # 从句：跳过逗号和空格，让从句引导词在下一行开头
                    split_pos += 1
                    if split_pos < len(sentence) and sentence[split_pos] == ' ':  # 跳过空格
                        split_pos += 1
                else:
                    # 非从句：跳过逗号和空格
                    split_pos += 1
                    if split_pos < len(sentence) and sentence[split_pos] == ' ':  # 保留一个空格在上一行
                        split_pos += 1
            elif sentence[split_pos] == ' ' and split_pos > 0 and sentence[split_pos - 1] == ',':
                # 如果正好在逗号后的空格处分行，则跳过这个空格
                split_pos += 1

        # 拆分句子（不修改任何标点或空白，只做换行）
        part1 = sentence[:split_pos]
        part2 = sentence[split_pos:]
        
        # 检查拆分后的部分是否太短（避免单个连接词成行）
        if len(part1.strip()) < 15 or len(part2.strip()) < 15:
            return [sentence]
        
        # 递归拆分：对每个部分独立评估
        result = []
        if part1 and len(part1) >= self.min_recursive_length:
            result.extend(self.split_sentence(part1, depth + 1))
        elif part1:
            result.append(part1)
            
        if part2 and len(part2) >= self.min_recursive_length:
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
    parser.add_argument(
        "--min-length", type=int, default=70, 
        help="最小递归长度阈值（默认70，低于此长度不再递归拆分）"
    )
    parser.add_argument(
        "--max-depth", type=int, default=8,
        help="最大递归深度（默认8，防止过度递归）"
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
    splitter = SmartSentenceSplitter(
        min_recursive_length=args.min_length,
        max_depth=args.max_depth
    )
    splitter.process_file(input_path, output_path)


if __name__ == "__main__":
    main()

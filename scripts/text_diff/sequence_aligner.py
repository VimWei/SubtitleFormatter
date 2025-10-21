"""
序列对齐模块
使用动态规划算法进行词汇序列对齐和差异检测
"""

from typing import List, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum


class DiffType(Enum):
    """差异类型枚举"""
    EQUAL = "equal"
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


@dataclass
class WordDifference:
    """词汇差异记录"""
    type: DiffType
    old_word: str
    new_word: str
    old_position: int
    new_position: int
    old_line: int
    new_line: int
    old_column: int
    new_column: int


@dataclass
class ComparisonResult:
    """比较结果"""
    differences: List[WordDifference]
    total_differences: int
    insertions: int
    deletions: int
    replacements: int
    equal_words: int
    similarity_ratio: float


class SequenceAligner:
    """序列对齐器"""
    
    def __init__(self):
        """初始化对齐器"""
        pass
    
    def align_sequences(self, old_words: List[str], new_words: List[str], 
                       old_positions: List[Dict], new_positions: List[Dict]) -> ComparisonResult:
        """
        对齐两个词汇序列并检测差异
        
        Args:
            old_words: 旧文本的词汇列表
            new_words: 新文本的词汇列表
            old_positions: 旧文本词汇位置信息
            new_positions: 新文本词汇位置信息
            
        Returns:
            result: 比较结果
        """
        # 使用LCS算法进行序列对齐
        lcs_matrix = self._build_lcs_matrix(old_words, new_words)
        alignment = self._backtrack_alignment(lcs_matrix, old_words, new_words)
        
        # 分析对齐结果，生成差异记录
        differences = self._analyze_alignment(alignment, old_positions, new_positions)
        
        # 计算统计信息
        stats = self._calculate_statistics(differences, len(old_words), len(new_words))
        
        return ComparisonResult(
            differences=differences,
            total_differences=stats['total_differences'],
            insertions=stats['insertions'],
            deletions=stats['deletions'],
            replacements=stats['replacements'],
            equal_words=stats['equal_words'],
            similarity_ratio=stats['similarity_ratio']
        )
    
    def _build_lcs_matrix(self, seq1: List[str], seq2: List[str]) -> List[List[int]]:
        """
        构建最长公共子序列矩阵
        
        Args:
            seq1: 第一个序列
            seq2: 第二个序列
            
        Returns:
            matrix: LCS矩阵
        """
        m, n = len(seq1), len(seq2)
        matrix = [[0] * (n + 1) for _ in range(m + 1)]
        
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if seq1[i-1] == seq2[j-1]:
                    matrix[i][j] = matrix[i-1][j-1] + 1
                else:
                    matrix[i][j] = max(matrix[i-1][j], matrix[i][j-1])
        
        return matrix
    
    def _backtrack_alignment(self, matrix: List[List[int]], 
                           seq1: List[str], seq2: List[str]) -> List[Tuple[str, str, str]]:
        """
        回溯构建对齐结果
        
        Args:
            matrix: LCS矩阵
            seq1: 第一个序列
            seq2: 第二个序列
            
        Returns:
            alignment: 对齐结果，每个元素为 (operation, word1, word2)
        """
        alignment = []
        i, j = len(seq1), len(seq2)
        
        while i > 0 or j > 0:
            if i > 0 and j > 0 and seq1[i-1] == seq2[j-1]:
                # 匹配
                alignment.append(('equal', seq1[i-1], seq2[j-1]))
                i -= 1
                j -= 1
            elif i > 0 and (j == 0 or matrix[i-1][j] >= matrix[i][j-1]):
                # 删除
                alignment.append(('delete', seq1[i-1], ''))
                i -= 1
            else:
                # 插入
                alignment.append(('insert', '', seq2[j-1]))
                j -= 1
        
        return list(reversed(alignment))
    
    def _analyze_alignment(self, alignment: List[Tuple[str, str, str]], 
                          old_positions: List[Dict], new_positions: List[Dict]) -> List[WordDifference]:
        """
        分析对齐结果，生成差异记录
        
        Args:
            alignment: 对齐结果
            old_positions: 旧文本位置信息
            new_positions: 新文本位置信息
            
        Returns:
            differences: 差异记录列表
        """
        differences = []
        old_idx = 0
        new_idx = 0
        
        for operation, old_word, new_word in alignment:
            if operation == 'equal':
                old_idx += 1
                new_idx += 1
            elif operation == 'delete':
                if old_idx < len(old_positions):
                    pos = old_positions[old_idx]
                    differences.append(WordDifference(
                        type=DiffType.DELETE,
                        old_word=old_word,
                        new_word='',
                        old_position=old_idx,
                        new_position=-1,
                        old_line=pos['line'],
                        new_line=-1,
                        old_column=pos['column'],
                        new_column=-1
                    ))
                old_idx += 1
            elif operation == 'insert':
                if new_idx < len(new_positions):
                    pos = new_positions[new_idx]
                    differences.append(WordDifference(
                        type=DiffType.INSERT,
                        old_word='',
                        new_word=new_word,
                        old_position=-1,
                        new_position=new_idx,
                        old_line=-1,
                        new_line=pos['line'],
                        old_column=-1,
                        new_column=pos['column']
                    ))
                new_idx += 1
            elif operation == 'replace':
                # 替换操作需要特殊处理
                old_pos = old_positions[old_idx] if old_idx < len(old_positions) else {}
                new_pos = new_positions[new_idx] if new_idx < len(new_positions) else {}
                
                differences.append(WordDifference(
                    type=DiffType.REPLACE,
                    old_word=old_word,
                    new_word=new_word,
                    old_position=old_idx,
                    new_position=new_idx,
                    old_line=old_pos.get('line', -1),
                    new_line=new_pos.get('line', -1),
                    old_column=old_pos.get('column', -1),
                    new_column=new_pos.get('column', -1)
                ))
                old_idx += 1
                new_idx += 1
        
        return differences
    
    def _calculate_statistics(self, differences: List[WordDifference], 
                            old_len: int, new_len: int) -> Dict[str, Any]:
        """
        计算统计信息
        
        Args:
            differences: 差异记录列表
            old_len: 旧文本词汇数量
            new_len: 新文本词汇数量
            
        Returns:
            stats: 统计信息字典
        """
        insertions = sum(1 for d in differences if d.type == DiffType.INSERT)
        deletions = sum(1 for d in differences if d.type == DiffType.DELETE)
        replacements = sum(1 for d in differences if d.type == DiffType.REPLACE)
        equal_words = min(old_len, new_len) - replacements
        
        total_differences = insertions + deletions + replacements
        total_words = max(old_len, new_len)
        similarity_ratio = (total_words - total_differences) / total_words if total_words > 0 else 1.0
        
        return {
            'total_differences': total_differences,
            'insertions': insertions,
            'deletions': deletions,
            'replacements': replacements,
            'equal_words': equal_words,
            'similarity_ratio': similarity_ratio
        }

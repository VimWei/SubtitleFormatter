import re
import spacy

class LineBreaker:
    """智能断行处理器"""
    
    def __init__(self, config):
        """初始化断行处理器
        
        Args:
            config: 配置字典，包含：
                   - max_width: 最大行宽
                   - nlp: 预加载的语言模型
                   - smart_wrap: 是否启用智能断行（可选，默认True）
        """
        self.config = config
        self.max_width = config['max_width']
        self.smart_wrap = config.get('smart_wrap', True)
        self.nlp = config['nlp'] if self.smart_wrap else None
        
    def process(self, sentences):
        """处理文本断行
        
        Args:
            sentences: 句子列表
            
        Returns:
            str: 处理后的文本
        """
        formatted_lines = []
        
        for sent in sentences:
            if len(sent) <= self.max_width:
                formatted_lines.append(sent)
            else:
                # 根据设置选择断行方式
                if self.smart_wrap:
                    lines = self._smart_wrap(sent)
                else:
                    lines = self._simple_wrap(sent)
                formatted_lines.extend(lines)
                
        return '\n'.join(formatted_lines)
        
    def _smart_wrap(self, sentence):
        """基于语法结构智能断行"""
        doc = self.nlp(sentence)
        lines = []
        current_tokens = []
        
        for token in doc:
            # 在语法边界处断行
            if current_tokens and self._is_break_point(token):
                line = self._process_line(current_tokens)
                if line:
                    lines.append(line)
                current_tokens = []
            
            current_tokens.append(token)
        
        # 处理最后一部分
        if current_tokens:
            line = self._process_line(current_tokens)
            if line:
                lines.append(line)
        
        return lines
        
    def _simple_wrap(self, sentence):
        """简单断行处理"""
        words = sentence.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            word_length = len(word)
            if current_length + word_length + len(current_line) <= self.max_width:
                current_line.append(word)
                current_length += word_length
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = word_length
        
        if current_line:
            lines.append(' '.join(current_line))
            
        return lines
        
    def _is_break_point(self, token):
        """判断是否是语法断点"""
        # 1. 并列连词
        if token.dep_ == 'cc':
            return True
        
        # 2. 从句标记
        if token.dep_ == 'mark':
            return True
        
        # 3. 长的介词短语
        if token.dep_ == 'prep' and len(list(token.children)) > 2:
            return True
        
        # 4. 转折词
        if token.text.lower() in {'but', 'however', 'nevertheless'}:
            return True
        
        return False
        
    def _process_line(self, tokens):
        """处理单行文本"""
        # 直接使用原始文本，保持原有格式
        text = ''.join(token.text_with_ws for token in tokens)
        return text.strip()
        
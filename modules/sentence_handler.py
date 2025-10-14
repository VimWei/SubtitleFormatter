import spacy
import re

class SentenceHandler:
    """智能断句处理器"""
    
    def __init__(self, config):
        """初始化断句处理器"""
        self.config = config
        self.language = config['language']
        self.nlp = config['nlp']
    
    def process(self, text):
        """处理文本断句"""
        # 使用已加载的模型进行处理
        doc = self.nlp(text)
        sentences = []
        current_text = ""
        
        for token in doc:
            # 保持原始空格
            space = token.whitespace_
            
            # 处理缩写词
            if token.text in {"'s", "n't", "'t", "'re", "'ve", "'ll", "'d", "'m"}:
                current_text = current_text.rstrip() + token.text + space
            # 处理标点符号
            elif token.text in {",", ".", "!", "?", ":", ";"}:
                current_text = current_text.rstrip() + token.text + space
            # 处理连字符
            elif token.text == "-":
                current_text = current_text.rstrip() + token.text
            # 正常单词
            else:
                current_text += token.text + space
            
            # 检查是否是句子结束
            if token.is_sent_end:
                # 确保句子有结束标点
                if current_text.strip() and current_text.strip()[-1] not in {'.', '!', '?'}:
                    current_text = current_text.rstrip() + '.' + ' '
                
                # 添加到结果中，确保每个句子是一个完整的单位
                if current_text.strip():
                    # 移除句子内的换行符，使其成为单行
                    current_text = ' '.join(current_text.strip().split())
                    sentences.append(current_text)
                current_text = ""
        
        # 处理最后一个句子
        if current_text.strip():
            if current_text.strip()[-1] not in {'.', '!', '?'}:
                current_text = current_text.rstrip() + '.'
            # 同样移除句子内的换行符
            current_text = ' '.join(current_text.strip().split())
            sentences.append(current_text)
        
        # 在返回结果前，将每句的首字母转为大写
        sentences = [s.strip() for s in sentences if s.strip()]
        sentences = [s[0].upper() + s[1:] if s else s for s in sentences]
        
        return sentences

    def _is_sentence_end(self, token):
        """判断是否是句子结束"""
        if token.is_sent_end:
            return True
        if token.text in {'.', '!', '?'}:
            return True
        return False

    def _fix_basic_punctuation(self, text):
        """修复基本标点和空格问题"""
        # 1. 修复缩写词
        fixes = [
            (r"(\w)\s+n\s*'\s*t\b", r"\1n't"),      # do n't -> don't
            (r"(\w)\s+'\s*s\b", r"\1's"),           # it 's -> it's
            (r"(\w)\s+'\s*m\b", r"\1'm"),           # I 'm -> I'm
            (r"(\w)\s+'\s*re\b", r"\1're"),         # you 're -> you're
            (r"(\w)\s+'\s*ve\b", r"\1've"),         # would 've -> would've
            (r"(\w)\s+'\s*ll\b", r"\1'll"),         # we 'll -> we'll
            (r"(\w)\s+'\s*d\b", r"\1'd"),           # he 'd -> he'd
            (r"gon\s+na\b", "gonna"),               # gon na -> gonna
            (r"(\w)\s*-\s*(\w)", r"\1-\2"),         # bee - tree -> bee-tree
        ]
        
        for pattern, replacement in fixes:
            text = re.sub(pattern, replacement, text)
        
        # 2. 修复标点周围的空格
        text = re.sub(r'\s+([,.!?:;])', r'\1', text)     # word , -> word,
        text = re.sub(r'([,.!?:;])\s*', r'\1 ', text)    # word,word -> word, word
        
        # 3. 修复重复的词和空格
        text = re.sub(r'\s+', ' ', text)                  # 多个空格变成一个
        text = re.sub(r'(\b\w+\b)(\s+\1\b)+', r'\1', text)  # 删除重复的词
        
        return text.strip()

    def _process_sentence(self, sent):
        """处理单个句子"""
        text = sent.text.strip()
        
        if not text:
            return None
        
        # 1. 确保句首大写
        if text[0].isalpha():
            text = text[0].upper() + text[1:]
        
        # 2. 确保句尾有标点
        if text[-1] not in {'.', '!', '?'}:
            # 如果是句子的结尾，添加句号
            if sent[-1].is_sent_end:
                text += '.'
            # 否则添加逗号
            elif not text[-1] in {',', ';', ':'}:
                text += ','
        
        return text

    def _should_end_with_period(self, token):
        """判断是否应该以句号结束"""
        # 1. 检查是否是文档的最后一个token
        if token.i == len(token.doc) - 1:
            return True
        
        # 2. 检查下一个token是否开始新句子
        next_token = token.doc[token.i + 1] if token.i < len(token.doc) - 1 else None
        if next_token and next_token.is_sent_start:
            return True
        
        # 3. 检查是否是完整陈述句的结尾
        if token.dep_ in {'ROOT', 'ccomp', 'xcomp'} and token.pos_ == 'VERB':
            # 检查是否有下一个并列句
            next_tokens = [t for t in token.rights if t.dep_ == 'cc']
            if not next_tokens:
                return True
            
        # 4. 检查特定的句子结束标记
        end_markers = {'okay', 'right', 'yes', 'no', 'thanks', 'please'}
        if token.text.lower() in end_markers:
            return True
        
        # 5. 检查是否是引号内的完整句子结尾
        if token.text in {'"', "'"}:
            prev_token = token.doc[token.i - 1] if token.i > 0 else None
            if prev_token and self._should_end_with_period(prev_token):
                return True
        
        return False

    def _is_sentence_start(self, token):
        """判断token是否是句子开始"""
        # 1. 检查是否是文档开始
        if token.i == 0:
            return True
        
        # 2. 检查是否是spaCy识别的句子开始
        if token.is_sent_start:
            return True
        
        # 3. 检查前一个token是否是句子结束标点
        prev_token = token.doc[token.i - 1] if token.i > 0 else None
        if prev_token and prev_token.text in {'.', '!', '?'}:
            return True
        
        # 4. 检查是否是特定的句子开始词
        sentence_starters = {'but', 'however', 'nevertheless', 'moreover', 'furthermore', 'therefore'}
        if token.text.lower() in sentence_starters and token.i > 0:
            return True
        
        return False

    def _fix_word_spacing(self, tokens):
        """修复单词之间的空格"""
        text = ''
        for i, token in enumerate(tokens):
            current_text = token.text.strip()
            
            # 跳过空token
            if not current_text:
                continue
            
            # 处理重复的单词
            if i > 0 and current_text == tokens[i-1].text:
                # 检查是否是有意重复（如 "very very" 或 "it's it's"）
                if not self._is_intentional_repeat(tokens[i-1], token):
                    continue
            
            # 处理单词之间的空格
            if i > 0:
                prev_text = tokens[i-1].text.strip()
                
                # 不需要空格的情况
                no_space_before = {
                    "'s", "n't", "'t", "'re", "'ve", "'ll", "'d", "'m",  # 缩写
                    ",", ".", "!", "?", ":", ";", ")", "]", "}",         # 标点
                    "-"                                                   # 连字符
                }
                
                no_space_after = {
                    "(", "[", "{", "$", "£", "€", "#", "@",              # 特殊字符
                    "-", "'"                                             # 连字符和撇号
                }
                
                needs_space = True
                
                # 检查是否需要空格
                if (current_text in no_space_before or
                    prev_text in no_space_after or
                    prev_text.endswith("-") or
                    current_text.startswith("-")):
                    needs_space = False
                    
                # 处理特殊情况
                if current_text == "'" and prev_text.lower() in {"it", "don", "won", "can", "didn"}:
                    needs_space = False
                    
                # 处理数字和单位
                if (prev_text.isdigit() and current_text in {"st", "nd", "rd", "th"}) or \
                   (current_text.isdigit() and prev_text in {"Chapter", "Section", "Part"}):
                    needs_space = True
                
                # 添加空格
                if needs_space:
                    text += ' '
            
            text += current_text
        
        # 修复常见问题
        text = self._fix_common_spacing_issues(text)
        return text

    def _fix_common_spacing_issues(self, text):
        """修复常见的空格问题"""
        # 1. 修复重复的空格
        text = ' '.join(text.split())
        
        # 2. 修复常见的词组
        common_phrases = {
            r'gon\s+na': 'gonna',
            r'wan\s+na': 'wanna',
            r'got\s+ta': 'gotta',
            r'kind\s+of': 'kind of',
            r'sort\s+of': 'sort of',
            r'out\s+of': 'out of',
            r'such\s+as': 'such as',
            r'rather\s+than': 'rather than',
            r'more\s+than': 'more than',
            r'less\s+than': 'less than',
            r'so\s+that': 'so that',
            r'even\s+though': 'even though',
            r'even\s+if': 'even if',
            r'as\s+if': 'as if',
            r'in\s+order': 'in order',
            r'no\s+one': 'no one',
            r'each\s+other': 'each other',
            r'one\s+another': 'one another'
        }
        
        for pattern, replacement in common_phrases.items():
            text = re.sub(pattern, replacement, text)
        
        # 3. 修复数字和单位之间的空格
        text = re.sub(r'(\d+)\s+([%°$£€¥])', r'\1\2', text)
        
        # 4. 修复重复的单词
        text = re.sub(r'\b(\w+)(\s+\1)+\b', r'\1', text)
        
        return text

    def _is_intentional_repeat(self, prev_token, current_token):
        """判断是否是有意的重复"""
        # 允许重复的词列表
        allowed_repeats = {
            'very', 'really', 'quite', 'so', 'too',  # 强调词
            'no', 'yes', 'yeah', 'oh', 'ah',         # 感叹词
            'bye', 'hey', 'hi', 'hello',             # 问候语
            'ha', 'haha', 'hehe',                    # 笑声
            'it\'s', 'that\'s', 'there\'s',          # 特定短语
        }
        
        # 检查是否在允许重复的列表中
        if prev_token.text.lower() in allowed_repeats:
            return True
        
        # 检查是否是重复的标点（如 "...")
        if prev_token.text in {'.', '!', '?', '-'}:
            return True
        
        # 检查是否是口语重复（通过词性标记）
        if prev_token.pos_ in {'INTJ', 'UH'}:  # 感叹词
            return True
        
        return False

    def _fix_contractions_and_punctuation(self, text):
        """修正缩写词和标点符号"""
        # 1. 处理缩写词
        contractions = {
            r"(\w)\s+n\s*'\s*t\b": r"\1n't",      # did n ' t -> didn't
            r"(\w)\s+'\s*s\b": r"\1's",           # it ' s -> it's
            r"(\w)\s+'\s*m\b": r"\1'm",           # I ' m -> I'm
            r"(\w)\s+'\s*re\b": r"\1're",         # you ' re -> you're
            r"(\w)\s+'\s*ve\b": r"\1've",         # would ' ve -> would've
            r"(\w)\s+'\s*ll\b": r"\1'll",         # we ' ll -> we'll
            r"(\w)\s+'\s*d\b": r"\1'd",           # he ' d -> he'd
            r"(\w)\s*-\s*timer": r"\1-timer",     # old - timer -> old-timer
            r"gon\s+na\b": r"gonna",              # gon na -> gonna
            r"I\s+'\s*m\b": "I'm",                # I ' m -> I'm
            r"i\s+'\s*m\b": "I'm"                 # i ' m -> I'm
        }
        
        for pattern, replacement in contractions.items():
            text = re.sub(pattern, replacement, text)
        
        # 2. 处理标点
        punctuation_rules = {
            r"\s+([,.!?:;])": r"\1",              # word , -> word,
            r"([,.!?:;])\s+": r"\1 ",             # word,word -> word, word
            r"\s+\.\s+": ". ",                    # word . -> word.
            r"(\w)\s+\.\s+(\w)": r"\1. \2",       # St . Patrick -> St. Patrick
            r"(\w)\s*-\s*(\w)": r"\1-\2"          # word - word -> word-word
        }
        
        for pattern, replacement in punctuation_rules.items():
            text = re.sub(pattern, replacement, text)
        
        # 3. 修复可能被错误合并的单词
        text = re.sub(r"(\w)([A-Z])", r"\1 \2", text)  # wordWord -> word Word
        
        # 4. 修复特殊情况
        text = re.sub(r"(\w)n't", r"\1n't", text)  # 确保n't前有空格
        text = re.sub(r"(\w)'s", r"\1's", text)    # 确保's前没有多余空格
        
        return text.strip()

    def _preprocess_text(self, text):
        """预处理文本"""
        # 确保输入是字符串
        if not isinstance(text, str):
            text = str(text)
        
        # 1. 合并多行
        text = ' '.join(line.strip() for line in text.split('\n') if line.strip())
        
        # 2. 删除口语停顿词
        fillers = {'um', 'uh', 'well'}
        words = text.split()
        text = ' '.join(w for w in words if w.lower() not in fillers)
        
        return text

    def _split_by_grammar(self, sent):
        """基于语法结构智能分句"""
        parts = []
        current_tokens = []
        
        for token in sent:
            # 检查是否需要在当前位置断句
            if current_tokens and (self._is_break_point(token) or self._should_start_new_sentence(token)):
                line = self._process_line(current_tokens)
                if line:
                    parts.append(line)
                current_tokens = []
            
            current_tokens.append(token)
        
        # 处理最后一部分
        if current_tokens:
            line = self._process_line(current_tokens)
            if line:
                parts.append(line)
        
        return parts

    def _should_start_new_sentence(self, token):
        """判断是否应该开始新句子"""
        # 1. 句子开头的连词
        if token.text.lower() in {'and', 'but', 'or', 'so', 'because', 'if', 'though', 'as'} and token.i > 0:
            # 检查是否完整的从句结构
            has_subject = False
            has_verb = False
            for child in token.head.subtree:
                if child.dep_ == 'nsubj':
                    has_subject = True
                elif child.dep_ == 'ROOT' and child.pos_ == 'VERB':
                    has_verb = True
            return has_subject and has_verb
        
        return False

    def _process_line(self, tokens):
        """处理单行文本"""
        if not tokens:
            return None
            
        # 获取原始文本
        text = ' '.join(t.text for t in tokens)
        
        # 修正标点和空格
        text = self._fix_contractions_and_punctuation(text)
        
        # 确保句首大写
        if text and text[0].isalpha():
            text = text[0].upper() + text[1:]
        
        # 确保句子有适当的标点
        text = text.strip()
        if text and not text[-1] in {'.', '!', '?', ','}:
            # 判断是否是句子结尾
            is_sentence_end = tokens[-1].i == len(tokens[-1].doc) - 1
            text += '.' if is_sentence_end else ','
        
        return text

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
        
        # 4. 特定的转折词和连接词
        break_words = {
            'however', 'nevertheless', 'moreover', 'furthermore',
            'therefore', 'thus', 'hence', 'consequently',
            'meanwhile', 'afterward', 'subsequently'
        }
        if token.text.lower() in break_words:
            return True
        
        # 5. 不在句首的but
        if token.text.lower() == 'but' and token.i > 0:
            return True
            
        return False 
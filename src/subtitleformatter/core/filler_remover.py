import warnings

import spacy


class FillerRemover:
    """停顿词处理类"""

    def __init__(self, config):
        """初始化停顿词处理器

        Args:
            config: 配置字典，包含：
                   - language: 语言设置
                   - nlp: 预加载的语言模型
        """
        self.config = config
        self.language = config["language"]
        self.nlp = config["nlp"]

        # 定义明确的停顿词
        if self.language == "zh":
            self.filler_words = {"嗯", "啊", "那个", "这个", "就是"}
            self.filler_patterns = {
                "所以": {
                    "is_filler": [r"所以\s", r"所以$", r"^所以\b"],
                    "is_valid": [r"所以说", r"所以才", r"正所以"],
                },
                "现在": {
                    "is_filler": [r"现在\s", r"现在$", r"^现在\b"],
                    "is_valid": [r"到现在", r"从现在", r"现在就"],
                },
            }
        else:
            self.filler_words = {"um", "uh", "well", "like", "you know"}
            self.filler_patterns = {
                "so": {
                    "is_filler": [r"so\s", r"so$", r"^so\b"],
                    "is_valid": [r"so that", r"and so on", r"if so"],
                },
                "now": {
                    "is_filler": [r"now\s", r"now$", r"^now\b"],
                    "is_valid": [r"by now", r"until now", r"from now"],
                },
                "ok": {
                    "is_filler": [r"ok\s", r"ok$", r"^ok\b"],
                    "is_valid": [r"is ok", r"ok with", r"if ok"],
                },
                "okay": {
                    "is_filler": [r"okay\s", r"okay$", r"^okay\b"],
                    "is_valid": [r"is okay", r"okay with", r"if okay"],
                },
            }

    def process(self, sentences):
        """处理句子列表，移除停顿词和重复词

        Args:
            sentences: 句子列表

        Returns:
            processed_sentences: 处理后的句子列表
            stats: 停顿词统计信息
        """
        import re
        from collections import Counter

        stats = Counter()

        processed_sentences = []
        for sentence in sentences:
            # 处理明确的停顿词
            words = sentence.split()
            processed_words = []
            i = 0
            while i < len(words):
                word = words[i].lower()

                # 检查连续重复词
                if i < len(words) - 1 and word == words[i + 1].lower():
                    stats["repeated_words"] = stats.get("repeated_words", 0) + 1
                    i += 1  # 跳过下一个重复的词
                    continue

                # 检查是否是明确的停顿词
                if word in self.filler_words:
                    stats[word] += 1
                    i += 1
                    continue

                # 检查上下文相关的词
                if word in self.filler_patterns:
                    # 获取上下文（向前和向后看2-3个词）
                    start = max(0, i - 2)
                    end = min(len(words), i + 3)
                    context = " ".join(words[start:end])

                    # 判断是否是停顿词用法
                    is_filler = any(
                        re.search(pattern, context, re.I)
                        for pattern in self.filler_patterns[word]["is_filler"]
                    )
                    is_valid = any(
                        re.search(pattern, context, re.I)
                        for pattern in self.filler_patterns[word]["is_valid"]
                    )

                    if is_filler and not is_valid:
                        stats[word] += 1
                        i += 1
                        continue

                processed_words.append(words[i])
                i += 1

            if processed_words:  # 只添加非空句子
                processed_sentences.append(" ".join(processed_words))

        return processed_sentences, stats

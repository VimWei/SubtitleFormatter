import spacy


class ModelManager:
    """语言模型管理器"""

    @staticmethod
    def get_model(config):
        """获取语言模型实例

        Args:
            config: 配置字典，包含：
                   - language: 语言设置 ('auto'/'en'/'zh')
                   - model_size: 模型大小 ('sm'/'md'/'lg')

        Returns:
            spacy.Language: 加载好的语言模型
        """
        language = config["language"]
        model_size = config["model_size"]

        # 确定模型名称
        if language == "auto" or language == "en":
            model_name = f"en_core_web_{model_size}"
        else:
            model_name = f"{language}_core_news_{model_size}"

        # 加载或下载模型
        try:
            nlp = spacy.load(model_name)
            print(f"已加载语言模型: {model_name}")
        except OSError:
            print(f"正在下载语言模型: {model_name}")
            spacy.cli.download(model_name)
            nlp = spacy.load(model_name)

        return nlp
